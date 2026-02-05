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
        fields = [
            "name",
            "description",
            "is_active",
            "youtube_link",
            "short_description",
            "description_flow",
            "description_eksempel",
            "description_aktiverede",
            "location",
            "image",
        ]

class AktivitetsTeamBookingAdminForm(forms.ModelForm):
    class Meta:
        model = models.AktivitetsTeamBooking
        fields = [
            "item", "team", "team_contact", "status", "start_date", 
            "start_time", "end_date", "end_time", "location", 
            "remarks", "remarks_internal",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# --- Inlines & Filters ---

class AssignedInline(TabularInline):
    # This must match your ManyToMany 'through' table
    model = models.AktivitetsTeamBooking.assigned_aktivitetsteam.through
    verbose_name = "Tilknyttet person"
    verbose_name_plural = "Tilknyttede personer"
    extra = 1
    
    # Unfold specific styling (optional but looks better)
    tab = True 

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # We check both 'volunteer' and 'user' just in case
        if db_field.name in ["volunteer", "user"]:
            kwargs["queryset"] = Volunteer.objects.filter(
                groups__name="AktivitetsTeamBookingTildeling",
                is_active=True
            )
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
        "name", "short_description", "is_active", "last_updated",
    ]
    readonly_fields = ["created", "last_updated"]
    search_fields = ['name', 'description', 'short_description', 'description_flow', 'description_eksempel', 'description_aktiverede']
    list_per_page = 100

@admin.register(models.AktivitetsTeamBooking)
class AktivitetsTeamBookingAdmin(ModelAdmin, ImportExportModelAdmin): # Combine Unfold and ImportExport
    resource_class = AktivitetsTeamBookingResource
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm # Unfold-ready export form
    form = AktivitetsTeamBookingAdminForm
    list_max_show_all = 500
    list_per_page = 25

    list_display = [
        "item", "team", 
        "formatted_team_contact", 
        "formatted_start_datetime", "formatted_end_datetime", "display_status", 
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
        ("Booking Status", {
            "fields": (
                "status",
            ),
        }),
        ("Booking Information", {
            "fields": (
                ("item", "team"),
                "team_contact",
            ),
        }),
        ("Date & Time", {
            "fields": (
                ("start_date", "start_time"),
                ("end_date", "end_time"),
            ),
        }),
        ("Location Details", {
            "description": "Klik på kortet for at sætte lokationen for aktiviteten.",
            "fields": (
                "location",
            ),
        }),
        ("Internal Notes", {
            "fields": (
                "remarks",
                "remarks_internal",
            ),
        }),
        ("Metadata", {
            "classes": ["collapse"],
            "fields": (
                ("created", "last_updated"), 
            ),
        }),
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