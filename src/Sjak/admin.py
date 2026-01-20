import csv
from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render

# Unfold & Import/Export
from unfold.admin import ModelAdmin
from unfold.decorators import action, display
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# Unfold Contrib for styled Import/Export forms
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm

# Models & Forms
from .models import SjakItem, SjakBooking, SjakItemType, SjakItemLocation
from .forms import SjakBookingForm, SjakItemForm

# --- Resources ---

class SjakItemResource(resources.ModelResource):
    class Meta:
        model = SjakItem
        fields = ('name', 'item_type__name', 'location__name', 'quantity_lager')

# --- Base Admin ---

class SjakBaseAdmin(ModelAdmin, ImportExportModelAdmin):
    """
    Base configuration for Sjak module using Unfold and Import/Export.
    """
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm
    
    actions = ["approve_selected", "reject_selected", "export_selected_raw"]

    @admin.action(description="Godkend valgte")
    def approve_selected(self, request, queryset):
        updated = queryset.update(status="Approved")
        self.message_user(request, f"{updated} bookinger er nu godkendt.", messages.SUCCESS)

    @admin.action(description="Afvis valgte")
    def reject_selected(self, request, queryset):
        updated = queryset.update(status="Rejected")
        self.message_user(request, f"{updated} bookinger er blevet afvist.", messages.WARNING)

    @admin.action(description="Eksporter valgte (CSV)")
    def export_selected_raw(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.model_name}_export.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

# --- Admin Classes ---

@admin.register(SjakItem)
class SjakItemAdmin(SjakBaseAdmin):
    resource_class = SjakItemResource
    list_display = ["display_image", "name", "display_item_type", "display_location", "quantity_lager", "last_updated"]
    list_filter = ["item_type", "location"]
    search_fields = ["name", "description"]

    @display(description="Billede")
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="40" height="40" class="rounded" />', obj.image.url)
        return "-"

    @display(description="Type", label=True)
    def display_item_type(self, obj):
        return obj.item_type.name if obj.item_type else "Ingen type"

    @display(description="Lokation", label=True)
    def display_location(self, obj):
        return obj.location.name if obj.location else "Lager"

@admin.register(SjakBooking)
class SjakBookingAdmin(SjakBaseAdmin):
    list_fullwidth = True
    list_display = [
        "item", "quantity", "team", 
        "display_status", "display_internal_status", 
        "formatted_times", "last_updated"
    ]
    list_filter = ["status", "status_internal", "team", "item", "start"]
    search_fields = ["item__name", "team__name", "team_contact__first_name"]
    
    # Custom Internal Status Actions
    actions = SjakBaseAdmin.actions + ["set_klar", "set_igang"]

    @display(description="Status", label={
        "Approved": "success", 
        "Pending": "warning", 
        "Rejected": "danger"
    })
    def display_status(self, obj):
        return obj.status

    @display(description="Intern Status", label={
        "Afventer": "info",
        "Igang": "warning",
        "Klar": "success",
        "Afsluttet": "neutral"
    })
    def display_internal_status(self, obj):
        return obj.status_internal

    @display(description="Tidsramme")
    def formatted_times(self, obj):
        return f"{obj.start.strftime('%d/%m')} - {obj.end.strftime('%d/%m')}"

    @admin.action(description="Sæt Intern status: Klar")
    def set_klar(self, request, queryset):
        queryset.update(status_internal="Klar")

    @admin.action(description="Sæt Intern status: Igang")
    def set_igang(self, request, queryset):
        queryset.update(status_internal="Igang")

@admin.register(SjakItemType)
class SjakItemTypeAdmin(SjakBaseAdmin):
    list_display = ["name", "created"]

@admin.register(SjakItemLocation)
class SjakItemLocationAdmin(SjakBaseAdmin):
    list_display = ["name", "created"]