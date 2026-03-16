import csv
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from unfold.admin import ModelAdmin, GenericTabularInline
from unfold.decorators import display
from unfold.contrib.import_export.forms import ImportForm, SelectableFieldsExportForm
from import_export.admin import ImportExportModelAdmin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from django_comments_xtd.models import XtdComment

from .models import SjakItem, SjakBooking, SjakItemType, SjakItemLocation, SjakTag
from .forms import SjakBookingForm, SjakItemForm


# ============================================================================
# IMPORT/EXPORT RESSOURCER
# ============================================================================

class CreateIfNotFoundWidget(ForeignKeyWidget):
    """Automatisk opret relaterede objekter hvis de ikke findes ved import."""
    
    def clean(self, value, row=None, **kwargs):
        if not value:
            return None
        obj, _ = self.model.objects.get_or_create(**{self.field: value})
        return obj


class SjakItemResource(resources.ModelResource):
    """Import/Export ressource for SjakItem med auto-oprettelse af relaterede objekter."""
    
    item_type = fields.Field(
        column_name='item_type',
        attribute='item_type',
        widget=CreateIfNotFoundWidget(SjakItemType, 'name')
    )
    location = fields.Field(
        column_name='location',
        attribute='location',
        widget=CreateIfNotFoundWidget(SjakItemLocation, 'name')
    )

    class Meta:
        model = SjakItem
        import_id_fields = ('name',)
        fields = ('name', 'item_type', 'location', 'quantity_lager', 'description')
        export_order = fields


# ============================================================================
# BASE ADMIN
# ============================================================================

class SjakBaseAdmin(ModelAdmin, ImportExportModelAdmin):
    """Basiskonfiguration for alle Sjak admin klasser."""
    
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm
    actions = ["approve_selected", "reject_selected", "export_selected_raw"]

    @admin.action(description="Godkend valgte")
    def approve_selected(self, request, queryset):
        """Godkend valgte bookinger."""
        updated = queryset.update(status="Approved")
        self.message_user(request, f"{updated} bookinger er nu godkendt.", messages.SUCCESS)

    @admin.action(description="Afvis valgte")
    def reject_selected(self, request, queryset):
        """Afvis valgte bookinger."""
        updated = queryset.update(status="Rejected")
        self.message_user(request, f"{updated} bookinger er blevet afvist.", messages.WARNING)

    @admin.action(description="Eksporter valgte (CSV)")
    def export_selected_raw(self, request, queryset):
        """Eksporter valgte elementer som CSV."""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.model_name}_export.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response


# ============================================================================
# KOMMENTAR INLINE
# ============================================================================

class CommentInline(GenericTabularInline):
    """Inline for tilføjelse/redigering af kommentarer på bookinger."""
    
    model = XtdComment
    ct_field = "content_type"
    ct_fk_field = "object_pk"
    extra = 1
    fields = ("user", "comment", "submit_date", "is_public")
    readonly_fields = ("submit_date", "user")

    def has_change_permission(self, request, obj=None):
        """Tillad kun forfatter eller superuser at redigere kommentarer."""
        if obj and isinstance(obj, XtdComment):
            return obj.user == request.user or request.user.is_superuser
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Tillad kun forfatter eller superuser at slette kommentarer."""
        if obj and isinstance(obj, XtdComment):
            return obj.user == request.user or request.user.is_superuser
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        """Indsæt nuværende bruger og site ID når kommentarer gemmes."""
        if not obj.user:
            obj.user = request.user
        if not obj.site_id:
            obj.site_id = getattr(settings, "SITE_ID", 1)
        if not obj.user_name:
            obj.user_name = request.user.get_full_name() or request.user.username
        if not obj.user_email:
            obj.user_email = request.user.email
        super().save_model(request, obj, form, change)


# ============================================================================
# SJAK TING ADMIN
# ============================================================================

@admin.register(SjakItem)
class SjakItemAdmin(SjakBaseAdmin):
    """Admin for håndtering af Sjak ting/udstyr."""
    
    resource_class = SjakItemResource
    list_display = ["name", "display_item_type", "display_location", "display_image", "quantity_lager", "last_updated"]
    list_filter = ["item_type", "location", "created"]
    search_fields = ["name", "description"]
    list_fullwidth = True
    date_hierarchy = "created"
    ordering = ["-last_updated"]
    list_per_page = 25

    @display(description="Billede")
    def display_image(self, obj):
        """Vis miniaturebillede af ting."""
        if obj.image:
            return format_html(
                '<img src="{}" width="40" height="40" class="rounded" />', 
                obj.image.url
            )
        return "-"

    @display(description="Type", label=True)
    def display_item_type(self, obj):
        """Vis tingtype eller 'Ingen type'."""
        return obj.item_type.name if obj.item_type else "Ingen type"

    @display(description="Lokation", label=True)
    def display_location(self, obj):
        """Vis lokation eller 'Lager'."""
        return obj.location.name if obj.location else "Lager"


# ============================================================================
# SJAK BOOKING ADMIN
# ============================================================================

@admin.register(SjakBooking)
class SjakBookingAdmin(SjakBaseAdmin):
    """Admin for håndtering af Sjak udstyrsbookinger."""
    
    inlines = [CommentInline]
    form = SjakBookingForm
    list_fullwidth = True
    date_hierarchy = "start"
    ordering = ["-start"]
    list_per_page = 30
    
    list_display = [
        "item", "quantity", "team",
        "display_status", "display_internal_status",
        "formatted_times", "last_updated"
    ]
    list_filter = ["status", "status_internal", "team", "item", "start"]
    search_fields = ["item__name", "team__name", "team_contact__first_name"]
    readonly_fields = ["image_preview"]
    actions = SjakBaseAdmin.actions + ["set_status_klar", "set_status_igang"]

    fieldsets = (
        ("Booking Information", {
            "fields": ("item", "quantity", "team", "team_contact", "assigned_sjak"),
            "description": "Grundlæggende bookingoplysninger"
        }),
        ("Datoer og Tider", {
            "fields": ("start", "start_time", "end", "end_time"),
            "classes": ("wide",)
        }),
        ("Status", {
            "fields": ("status", "status_internal"),
            "description": "Booking- og internt arbejdsstatus"
        }),
        ("Noter og Billede", {
            "fields": ("remarks", "image", "image_preview"),
        }),
    )

    # ---- Visningsmetoder ----

    @display(description="Status", label={
        "Approved": "success",
        "Pending": "warning",
        "Rejected": "danger"
    })
    def display_status(self, obj):
        """Vis bookingstatus med farve."""
        return obj.status

    @display(description="Intern Status", label={
        "Afventer": "info",
        "Igang": "warning",
        "Klar": "success",
        "Afsluttet": "neutral"
    })
    def display_internal_status(self, obj):
        """Vis internt status med farve."""
        return obj.status_internal

    @display(description="Tidsramme")
    def formatted_times(self, obj):
        """Vis datointervallet i kompakt format."""
        return f"{obj.start.strftime('%d/%m')} - {obj.end.strftime('%d/%m')}"

    def image_preview(self, obj):
        """Vis forhåndsvisning af bookingbillede hvis tilgængeligt."""
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="max-height: 200px; border-radius: 8px;" />'
            )
        return "Intet billede"

    image_preview.short_description = "Forhåndsvisning"

    # ---- Brugerdefinerede handlinger ----

    @admin.action(description="Sæt Intern status: Klar")
    def set_status_klar(self, request, queryset):
        """Sæt internt status til 'Klar' for valgte bookinger."""
        count = queryset.update(status_internal="Klar")
        self.message_user(request, f"{count} booking(er) sat til 'Klar'.", messages.SUCCESS)

    @admin.action(description="Sæt Intern status: Igang")
    def set_status_igang(self, request, queryset):
        """Sæt internt status til 'Igang' for valgte bookinger."""
        count = queryset.update(status_internal="Igang")
        self.message_user(request, f"{count} booking(er) sat til 'Igang'.", messages.SUCCESS)


# ============================================================================
# SIMPLE ADMIN KLASSER
# ============================================================================

@admin.register(SjakItemType)
class SjakItemTypeAdmin(SjakBaseAdmin):
    """Admin for tingtyper/kategorier."""
    list_display = ["name", "created"]
    list_fullwidth = True
    ordering = ["name"]


@admin.register(SjakItemLocation)
class SjakItemLocationAdmin(SjakBaseAdmin):
    """Admin for lagerlokaliteter."""
    list_display = ["name", "created"]
    list_fullwidth = True
    ordering = ["name"]


@admin.register(SjakTag)
class SjakTagAdmin(SjakBaseAdmin):
    """Admin for booking-mærker."""
    list_display = ["name", "color", "created"]
    fields = ["name", "color"]
    list_fullwidth = True
    ordering = ["name"]