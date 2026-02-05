import csv
from django.contrib import admin, messages
from django.http import HttpResponse

# Unfold & Import/Export
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

# Unfold Contrib for styled Import/Export forms
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm

# Comments
from django_comments_xtd.models import XtdComment
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import TeknikItem, TeknikBooking, TeknikType
from organization.models import Team, Volunteer

# --- Resources ---

class TeknikBookingResource(resources.ModelResource):
    item = fields.Field(column_name='Item', attribute='item', widget=ForeignKeyWidget(TeknikItem, 'name'))
    team = fields.Field(column_name='Team', attribute='team', widget=ForeignKeyWidget(Team, 'name'))
    team_contact = fields.Field(column_name='Kontakt', attribute='team_contact', widget=ForeignKeyWidget(Volunteer, 'first_name'))

    class Meta:
        model = TeknikBooking
        fields = (
            'id', 'item', 'quantity', 'team', 'team_contact', 
            'start_date', 'start_time', 'end_date', 'end_time', 
            'status', 'assistance_needed', 'delivery_needed'
        )

# --- Inlines ---

class TeknikCommentInline(GenericTabularInline):
    model = XtdComment
    # These two lines fix the (admin.E303) error:
    ct_field = "content_type"
    ct_fk_field = "object_pk" 
    
    extra = 0
    classes = ["tab"] 
    fields = ('user', 'comment', 'submit_date', 'is_public', 'is_removed')
    readonly_fields = ('submit_date', 'user')

# --- Base Admin ---

class TeknikBaseAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm
    
    actions = ["approve_selected", "reject_selected"]

    @admin.action(description="Godkend valgte")
    def approve_selected(self, request, queryset):
        queryset.update(status="Approved")
        self.message_user(request, "Valgte bookinger er godkendt.", messages.SUCCESS)

    @admin.action(description="Afvis valgte")
    def reject_selected(self, request, queryset):
        queryset.update(status="Rejected")
        self.message_user(request, "Valgte bookinger er afvist.", messages.WARNING)

# --- Admin Classes ---
@admin.register(TeknikBooking)
class TeknikBookingAdmin(TeknikBaseAdmin):
    resource_class = TeknikBookingResource
    list_fullwidth = True
    
    inlines = [TeknikCommentInline]
    
    list_display = [
        "item", "quantity", "team", "display_status",
        "formatted_start", "assistance_badge", "delivery_badge"
    ]

    fields = [
        ("item", "status"),
        ("team", "quantity"),
        ("start_date", "start_time"),
        ("end_date", "end_time"),
        "team_contact", 
        ("assistance_needed", "delivery_needed"),
        "remarks_internal",
        "location",
    ]

    # REMOVE the 'fields = [...]' line entirely. 
    # It was causing the unhashable type error and conflict.

    list_filter = ["status", "item", "team", "start_date"]
    search_fields = ["item__name", "team__name", "team_contact__first_name"]

    @display(description="Status", label={
        "Approved": "success", "Pending": "warning", "Rejected": "danger",
    })
    def display_status(self, obj):
        return obj.status

    @display(description="Start")
    def formatted_start(self, obj):
        return f"{obj.start_date.strftime('%d/%m')} {obj.start_time.strftime('%H:%M')}"

    @display(description="Assistance", label={"True": "info", "False": "neutral"})
    def assistance_badge(self, obj):
        return "Ja" if obj.assistance_needed else "Nej"

    @display(description="Levering", label={"True": "info", "False": "neutral"})
    def delivery_badge(self, obj):
        return "Ja" if obj.delivery_needed else "Nej"

@admin.register(TeknikItem)
class TeknikItemAdmin(TeknikBaseAdmin):
    list_display = ["name", "description", "last_updated"]
    search_fields = ["name", "description"]

@admin.register(TeknikType)
class TeknikTypeAdmin(TeknikBaseAdmin):
    list_display = ["name", "created"]