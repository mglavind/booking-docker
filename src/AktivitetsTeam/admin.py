from django.contrib import admin, messages
from django import forms
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from django.http import HttpResponseRedirect, HttpResponse
from organization.models import Volunteer
from . import models
from django.contrib.admin import SimpleListFilter
from geopy.geocoders import Nominatim
from django.urls import path, URLPattern
from django.shortcuts import render
from typing import List
from utils.ical_utils import convert_to_ical, export_selected_to_ical, send_ical_via_email
import csv
from django.conf import settings

from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import action, display

from . import models


class AktivitetsTeamItemAdminForm(forms.ModelForm):

    class Meta:
        model = models.AktivitetsTeamItem
        fields = "__all__"

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()

class AktivitetsTeamItemAdmin(ModelAdmin):
    form = AktivitetsTeamItemAdminForm
    list_display = [
        "name",
        "description",
        "youtube_link",
        "description_aktiverede",
        "description_eksempel",
        "description_flow",
        "created",
        "last_updated",
    ]
    readonly_fields = [
        "created",
        "last_updated",
    ]
    search_fields = ['name', 'description']
    actions = ["export_to_csv"]
    list_per_page = 25
    list_max_show_all = 500

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=aktivitetsteam_items.csv"
        response.write(u'\ufeff'.encode('utf8'))

        writer = csv.writer(response, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow([
            "name",
            "description",
            "short_description",
            "youtube_link",
            "description_aktiverede",
            "description_eksempel",
            "description_flow",
        ])

        for booking in queryset:
            writer.writerow([
                booking.name,
                booking.description,
                booking.short_description,
                booking.youtube_link,
                booking.description_aktiverede,
                booking.description_eksempel,
                booking.description_flow,
            ])

        return response
    export_to_csv.short_description = "Eksporter valgte til CSV"

    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls
    
    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]

            if not csv_file.name.endswith(".csv"):
                messages.warning(request, "Wrong file type was uploaded. Please upload a CSV file.")
                return HttpResponseRedirect(request.path_info)

            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")

            for line in csv_data:
                fields = line.split(";")
                name = fields[0]
                description = fields[1]
                short_description = fields[2]
                youtube_link = fields[3]
                description_aktiverede = fields[4]
                description_eksempel = fields[5]
                description_flow = fields[6]

                # Check if the name is unique
                if models.AktivitetsTeamItem.objects.filter(name=name).exists():
                    messages.warning(request, f"Item with name '{name}' already exists.")
                    continue

                form_data = {
                    "name": name,
                    "description": description,
                    "short_description": short_description,
                    "youtube_link": youtube_link,
                    "description_aktiverede": description_aktiverede,
                    "description_eksempel": description_eksempel,
                    "description_flow": description_flow,
                }

                # Create a LocationItemAdminForm instance with the modified form_data
                form = AktivitetsTeamItemAdminForm(form_data)

                if form.is_valid():
                    # Save the LocationItem instance
                    location_item = form.save()

                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        error_messages.append(f"Field '{field}': {'; '.join(map(str, errors))}")
                    error_message = "; ".join(error_messages)
                    messages.warning(request, f"Invalid data in CSV: {error_message}")

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)


class AktivitetsTeamBookingAdminForm(forms.ModelForm):

    class Meta:
        model = models.AktivitetsTeamBooking
        fields = [
            "item",
            "team",
            "team_contact",
            "status",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "location",
            "remarks",
            "remarks_internal",
            "latitude",
            "longitude",
            "address",
        ]

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for latitude and longitude if not provided
        if not self.instance.pk:
            self.fields['latitude'].initial = '56.114951'
            self.fields['longitude'].initial = '9.655592'
            self.fields['status'].initial = 'Pending'
            self.fields['address'].initial = 'FDF Friluftscenter Sletten, Bøgedalsvej, Bøgedal, Skanderborg Kommune, Region Midtjylland, Danmark'


class AssignedInline(TabularInline):
    model = models.AktivitetsTeamBooking.assigned_aktivitetsteam.through
    verbose_name = "Tilknyttet Aktivitetsteam"
    verbose_name_plural = "Tilknyttede Aktivitetsteam"
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "volunteer":
            # Get or create the group
            group, created = Group.objects.get_or_create(name="AktivitetstTeamBookingTildeling")
            kwargs["queryset"] = group.user_set.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AssignedAktivitetsteamFilter(SimpleListFilter):
    title = 'Assigned Aktivitetsteam'
    parameter_name = 'assigned_aktivitetsteam'

    def lookups(self, request, model_admin):
        # Provide the filter options
        volunteers = Volunteer.objects.filter(groups__name="AktivitetstTeamBookingTildeling", is_active=True)
        return [(volunteer.id, volunteer.first_name) for volunteer in volunteers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(assigned_aktivitetsteam__id=self.value())
        return queryset


class AktivitetsTeamBookingAdmin(ModelAdmin):
    form = AktivitetsTeamBookingAdminForm
    list_max_show_all = 500
    list_per_page = 25

    @display(description="Team Contact", ordering="team_contact__first_name")
    def formatted_team_contact(self, obj):
        return obj.team_contact.first_name

    @display(description="Start Date & Time", ordering="start_date")
    def formatted_start_datetime(self, obj):
        formatted_date = obj.start.strftime("%d/%m")
        formatted_time = obj.start.strftime("%H:%M")
        return f"{formatted_date} - {formatted_time}"

    @display(description="End Date & Time", ordering="end_date")
    def formatted_end_datetime(self, obj):
        formatted_date = obj.end.strftime("%d/%m")
        formatted_time = obj.end.strftime("%H:%M")
        return f"{formatted_date} - {formatted_time}"

    @display(description="Last Updated", ordering="last_updated")
    def formatted_last_updated(self, obj):
        formatted_date = obj.last_updated.strftime("%d/%m")
        formatted_time = obj.last_updated.strftime("%H:%M")
        return f"{formatted_date} - {formatted_time}"

    list_display = [
        "formatted_start_datetime",
        "item",
        "team",
        "formatted_team_contact",
        "status",
        "formatted_end_datetime",
        "address",
    ]
    
    readonly_fields = [
        "created",
        "last_updated",
    ]
    
    list_filter = (
        ('status', ChoiceDropdownFilter),
        ('item', RelatedDropdownFilter),
        ('team', RelatedDropdownFilter),
        AssignedAktivitetsteamFilter,
    )
    
    actions = [
        "approve_bookings",
        "reject_bookings",
        "export_to_csv",
        'export_selected_to_ical_action',
        'send_ical_via_email_action'
    ]
    
    search_fields = ['item__name', 'team__name']
    
    inlines = [AssignedInline]
    
    exclude = ["members"]

    fieldsets = (
        ("Booking Information", {
            "fields": ("item", "team", "team_contact", "status")
        }),
        ("Date & Time", {
            "fields": ("start_date", "start_time", "end_date", "end_time")
        }),
        ("Location", {
            "fields": ("location", "latitude", "longitude", "address")
        }),
        ("Notes", {
            "fields": ("remarks", "remarks_internal")
        }),
        ("Metadata", {
            "fields": ("created", "last_updated")
        }),
    )

    @action(description="Approve selected bookings")
    def approve_bookings(self, request, queryset):
        for booking in queryset:
            booking.status = "Approved"
            booking.save()
        self.message_user(request, f"{queryset.count()} booking(s) approved.")

    @action(description="Reject selected bookings")
    def reject_bookings(self, request, queryset):
        for booking in queryset:
            booking.status = "Rejected"
            booking.save()
        self.message_user(request, f"{queryset.count()} booking(s) rejected.")

    @action(description="Export selected bookings to CSV")
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=aktivitetsteam_bookings.csv"
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        


        for booking in queryset:
            writer.writerow([
                booking.item,
                booking.team,
                booking.team_contact,
                booking.start_date,
                booking.start_time,
                booking.end_date,
                booking.end_time,
                booking.location,
                booking.status,
                booking.remarks,
                booking.assigned_aktivitetsteam,
                booking.remarks_internal,
            ])

        return response

    def save_model(self, request, obj, form, change):
        latitude = form.cleaned_data.get('latitude')
        longitude = form.cleaned_data.get('longitude')
        
        if latitude and longitude:
            geolocator = Nominatim(user_agent="SKSBooking/1.0 (slettenbooking@gmail.com)")
            try:
                location = geolocator.reverse((latitude, longitude))
                if location:
                    obj.address = location.address
            except Exception as e:
                messages.warning(request, f"Could not reverse geocode: {str(e)}")
        
        obj.save()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        object = self.get_object(request, object_id)
        extra_context['latitude'] = object.latitude if object.latitude is not None else 56.1145
        extra_context['longitude'] = object.longitude if object.longitude is not None else 9.66427
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    @action(description="Export selected bookings to iCal")
    def export_selected_to_ical_action(self, request, queryset):
        ical_content = export_selected_to_ical(queryset)
        response = HttpResponse(ical_content, content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename="bookings.ics"'
        return response

    @action(description="Send iCal via email to assigned aktivitetsteam")
    def send_ical_via_email_action(self, request, queryset):
        email_template = "AktivitetsTeam/ical_email_template.html"
        from_email = settings.DEFAULT_FROM_EMAIL
        send_ical_via_email(queryset, email_template, from_email)
        self.message_user(request, f"Emails sent for {queryset.count()} bookings.")


admin.site.register(models.AktivitetsTeamItem, AktivitetsTeamItemAdmin)
admin.site.register(models.AktivitetsTeamBooking, AktivitetsTeamBookingAdmin)