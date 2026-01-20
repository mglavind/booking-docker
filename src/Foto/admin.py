from django.contrib import admin, messages
from django.http import HttpResponse
from unfold.admin import ModelAdmin
from unfold.decorators import display
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm
from icalendar import Calendar, Event
from datetime import datetime

from .models import FotoItem, FotoBooking

# --- Resources ---

class FotoBookingResource(resources.ModelResource):
    class Meta:
        model = FotoBooking
        fields = ('id', 'item__name', 'team__name', 'location', 'start_date', 'status')

# --- Admin Classes ---

@admin.register(FotoBooking)
class FotoBookingAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_class = FotoBookingResource
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm
    
    list_fullwidth = True
    list_display = [
        "item", "display_status", "location", "formatted_start", "formatted_end", "last_updated"
    ]
    list_filter = ["status", "item", "team"]
    search_fields = ["item__name", "location", "remarks"]
    readonly_fields = ["created", "last_updated"]
    actions = ["approve_selected", "reject_selected", "export_selected_to_ical"]

    @display(description="Status", label={
        "Approved": "success", "Pending": "warning", "Rejected": "danger",
    })
    def display_status(self, obj):
        return obj.status

    @display(description="Start")
    def formatted_start(self, obj):
        return f"{obj.start_date.strftime('%d/%m')} {obj.start_time.strftime('%H:%M')}"

    @display(description="Slut")
    def formatted_end(self, obj):
        return f"{obj.end_date.strftime('%d/%m')} {obj.end_time.strftime('%H:%M')}"

    @admin.action(description="Godkend valgte")
    def approve_selected(self, request, queryset):
        queryset.update(status="Approved")
        self.message_user(request, "Foto bookinger godkendt.", messages.SUCCESS)

    @admin.action(description="Afvis valgte")
    def reject_selected(self, request, queryset):
        queryset.update(status="Rejected")
        self.message_user(request, "Foto bookinger afvist.", messages.WARNING)

    @admin.action(description="Eksporter til iCal")
    def export_selected_to_ical(self, request, queryset):
        calendar = Calendar()
        for booking in queryset:
            event = Event()
            event.add('summary', f"Foto: {booking.item} v. {booking.location}")
            start = datetime.combine(booking.start_date, booking.start_time)
            end = datetime.combine(booking.end_date, booking.end_time)
            event.add('dtstart', start)
            event.add('dtend', end)
            calendar.add_component(event)
        
        response = HttpResponse(calendar.to_ical(), content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename="foto_bookings.ics"'
        return response

@admin.register(FotoItem)
class FotoItemAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ["name", "description", "last_updated"]
    search_fields = ["name"]