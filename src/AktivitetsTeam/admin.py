from django.contrib import admin, messages
from django import forms
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from django.http import HttpResponseRedirect, HttpResponse
from organization.models import Volunteer
from . import models
from django.contrib.admin import SimpleListFilter
from geopy.geocoders import Nominatim
from django.urls import path
from django.shortcuts import render
from typing import List
from utils.ical_utils import convert_to_ical, export_selected_to_ical, send_ical_via_email
import csv
from django.conf import settings

# Unfold & Import/Export
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action, display
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm
from django.contrib.auth.models import Group

# --- Resources ---

class AktivitetsTeamItemResource(resources.ModelResource):
    class Meta:
        model = models.AktivitetsTeamItem
        fields = (
            "name", "description", "short_description", "youtube_link", 
            "description_aktiverede", "description_eksempel", "description_flow"
        )
        # Empty tuple ensures every row in CSV creates a new DB record (allows duplicates)
        import_id_fields = () 
        export_order = fields

    def before_import_row(self, row, **kwargs):
        # Clean up leading/trailing accidental spaces but keep spaces between words
        for field in self.get_export_fields():
            column_name = field.column_name
            if column_name in row and row[column_name]:
                row[column_name] = str(row[column_name]).strip()

class AktivitetsTeamBookingResource(resources.ModelResource):
    class Meta:
        model = models.AktivitetsTeamBooking
        fields = (
            "item__name", "team__name", "team_contact__first_name", 
            "status", "start_date", "start_time", "end_date", "end_time", 
            "location", "remarks", "remarks_internal"
        )
        export_order = fields

# --- Base Admin ---

class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    """
    Common base for Unfold and Import/Export features.
    """
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm

# --- Forms ---

class AktivitetsTeamItemAdminForm(forms.ModelForm):
    class Meta:
        model = models.AktivitetsTeamItem
        fields = "__all__"

class AktivitetsTeamBookingAdminForm(forms.ModelForm):
    class Meta:
        model = models.AktivitetsTeamBooking
        fields = [
            "item", "team", "team_contact", "status", "start_date", 
            "start_time", "end_date", "end_time", "location", 
            "remarks", "remarks_internal", "latitude", "longitude", "address",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['latitude'].initial = '56.114951'
            self.fields['longitude'].initial = '9.655592'
            self.fields['status'].initial = 'Pending'
            self.fields['address'].initial = 'FDF Friluftscenter Sletten, Bøgedalsvej, Bøgedal, Skanderborg Kommune, Region Midtjylland, Danmark'

# --- Inlines & Filters ---

class AssignedInline(TabularInline):
    model = models.AktivitetsTeamBooking.assigned_aktivitetsteam.through
    verbose_name = "Tilknyttet Aktivitetsteam"
    verbose_name_plural = "Tilknyttede Aktivitetsteam"
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "volunteer":
            group, _ = Group.objects.get_or_create(name="AktivitetsTeamBookingTildeling")
            kwargs["queryset"] = group.user_set.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class AssignedAktivitetsteamFilter(SimpleListFilter):
    title = 'Assigned Aktivitetsteam'
    parameter_name = 'assigned_aktivitetsteam'

    def lookups(self, request, model_admin):
        volunteers = Volunteer.objects.filter(groups__name="AktivitetsTeamBookingTildeling", is_active=True)
        return [(volunteer.id, volunteer.first_name) for volunteer in volunteers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assigned_aktivitetsteam__id=self.value())
        return queryset

# --- Admin Registrations ---

@admin.register(models.AktivitetsTeamItem)
class AktivitetsTeamItemAdmin(BaseAdmin):
    resource_class = AktivitetsTeamItemResource
    form = AktivitetsTeamItemAdminForm
    list_display = [
        "name", "description", "youtube_link", 
        "description_aktiverede", "created", "last_updated",
    ]
    readonly_fields = ["created", "last_updated"]
    search_fields = ['name', 'description']
    list_per_page = 25

@admin.register(models.AktivitetsTeamBooking)
class AktivitetsTeamBookingAdmin(BaseAdmin):
    resource_class = AktivitetsTeamBookingResource
    form = AktivitetsTeamBookingAdminForm
    list_max_show_all = 500
    list_per_page = 25

    list_display = [
        "formatted_start_datetime", "item", "team", 
        "formatted_team_contact", "display_status", 
        "formatted_end_datetime", "address",
    ]
    
    readonly_fields = ["created", "last_updated"]
    list_filter = (
        ('status', ChoiceDropdownFilter),
        ('item', RelatedDropdownFilter),
        ('team', RelatedDropdownFilter),
        AssignedAktivitetsteamFilter,
    )
    
    actions = [
        "approve_bookings", "reject_bookings", 
        'export_selected_to_ical_action', 'send_ical_via_email_action'
    ]
    
    search_fields = ['item__name', 'team__name']
    inlines = [AssignedInline]
    exclude = ["members"]

    fieldsets = (
        ("Booking Information", {"fields": ("item", "team", "team_contact", "status")}),
        ("Date & Time", {"fields": ("start_date", "start_time", "end_date", "end_time")}),
        ("Location", {"fields": ("location", "latitude", "longitude", "address")}),
        ("Notes", {"fields": ("remarks", "remarks_internal")}),
        ("Metadata", {"fields": ("created", "last_updated")}),
    )

    @display(description="Status", label={
        "Approved": "success", "Pending": "warning", "Rejected": "danger",
    })
    def display_status(self, obj):
        return obj.status

    @display(description="Team Contact", ordering="team_contact__first_name")
    def formatted_team_contact(self, obj):
        return obj.team_contact.first_name if obj.team_contact else "-"

    @display(description="Start", ordering="start_date")
    def formatted_start_datetime(self, obj):
        return obj.start_date.strftime("%d/%m") + " - " + obj.start_time.strftime("%H:%M")

    @display(description="End", ordering="end_date")
    def formatted_end_datetime(self, obj):
        return obj.end_date.strftime("%d/%m") + " - " + obj.end_time.strftime("%H:%M")

    @action(description="Approve selected bookings")
    def approve_bookings(self, request, queryset):
        updated = queryset.update(status="Approved")
        self.message_user(request, f"{updated} booking(s) approved.", messages.SUCCESS)

    @action(description="Reject selected bookings")
    def reject_bookings(self, request, queryset):
        updated = queryset.update(status="Rejected")
        self.message_user(request, f"{updated} booking(s) rejected.", messages.WARNING)

    def save_model(self, request, obj, form, change):
        latitude = form.cleaned_data.get('latitude')
        longitude = form.cleaned_data.get('longitude')
        if latitude and longitude:
            geolocator = Nominatim(user_agent="SKSBooking/1.0")
            try:
                location = geolocator.reverse((latitude, longitude))
                if location:
                    obj.address = location.address
            except Exception as e:
                messages.warning(request, f"Could not reverse geocode: {str(e)}")
        obj.save()

    @action(description="Export selected bookings to iCal")
    def export_selected_to_ical_action(self, request, queryset):
        ical_content = export_selected_to_ical(queryset)
        response = HttpResponse(ical_content, content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename="bookings.ics"'
        return response

    @action(description="Send iCal via email")
    def send_ical_via_email_action(self, request, queryset):
        email_template = "AktivitetsTeam/ical_email_template.html"
        send_ical_via_email(queryset, email_template, settings.DEFAULT_FROM_EMAIL)
        self.message_user(request, f"Emails sent for {queryset.count()} bookings.")