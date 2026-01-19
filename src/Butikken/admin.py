import csv
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.http import HttpResponse

# Unfold & Import/Export
from unfold.admin import ModelAdmin, TabularInline 
from unfold.decorators import action, display
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# Unfold Contrib for styled Import/Export forms
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm

# Models & Forms
from .models import (
    ButikkenItem, ButikkenBooking, ButikkenItemType, 
    Day, Recipe, Meal, Option, MealBooking, 
    MealPlan, MealOption, TeamMealPlan
)
from .forms import ButikkenBookingForm, MealPlanForm

# --- Resources ---

class ButikkenItemResource(resources.ModelResource):
    class Meta:
        model = ButikkenItem
        fields = ('id', 'name', 'type', 'description', 'content_normal', 'content_unit')
        import_id_fields = ('name',)

class TeamMealPlanResource(resources.ModelResource):
    class Meta:
        model = TeamMealPlan
        fields = ('id', 'team__name', 'meal_plan__name', 'meal_option__recipe__name', 'status')

# --- Base Admin with Universal Features ---

class BaseAdmin(ModelAdmin, ImportExportModelAdmin):
    """
    Inherit from this to get selectable export/import 
    and bulk approve/reject/export actions automatically.
    """
    import_form_class = ImportForm
    export_form_class = SelectableFieldsExportForm
    
    # Raw Django Actions (Selection via Checkboxes)
    actions = ["approve_selected", "reject_selected", "export_selected_raw"]

    @admin.action(description="Godkend valgte")
    def approve_selected(self, request, queryset):
        updated = queryset.update(status="Approved")
        self.message_user(request, f"{updated} elementer er nu godkendt.", messages.SUCCESS)

    @admin.action(description="Afvis valgte")
    def reject_selected(self, request, queryset):
        updated = queryset.update(status="Rejected")
        self.message_user(request, f"{updated} elementer er blevet afvist.", messages.WARNING)

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

# --- Inlines ---

class MealOptionInline(TabularInline):
    model = MealOption
    extra = 1
    tab = True 

# --- Admin Classes ---

@admin.register(ButikkenItem)
class ButikkenItemAdmin(BaseAdmin):
    resource_class = ButikkenItemResource
    list_display = ["name", "display_type", "display_content", "last_updated"]
    list_filter = ["type"]
    search_fields = ["name", "description"]

    @display(description="Type", label=True)
    def display_type(self, obj):
        return obj.type

    @display(description="Indhold")
    def display_content(self, obj):
        return f"{obj.content_normal} {obj.content_unit}" if obj.content_normal else "-"

@admin.register(ButikkenBooking)
class ButikkenBookingAdmin(BaseAdmin):
    form = ButikkenBookingForm
    list_fullwidth = True
    # FIXED: 'for_meal' used directly as it's a field in your model
    list_display = ["item", "display_status", "team", "for_meal", "formatted_start", "quantity_with_unit"]
    list_filter = ["status", "for_meal", "team", "item", "start"]
    
    @display(description="Status", label={
        "Approved": "success", "Pending": "warning", "Rejected": "danger", "Udleveret": "info",
    })
    def display_status(self, obj):
        return obj.status

    @display(description="Mængde")
    def quantity_with_unit(self, obj):
        return f"{obj.quantity} {obj.unit}"

    @display(description="Afhentning")
    def formatted_start(self, obj):
        return f"{obj.start.strftime('%d/%m')} kl. {obj.start_time.strftime('%H:%M')}"

@admin.register(TeamMealPlan)
class TeamMealPlanAdmin(BaseAdmin):
    resource_class = TeamMealPlanResource
    list_display = ["team", "meal_plan", "meal_option", "display_status", "last_updated"]
    list_filter = ["status", "team"]

    @display(description="Status", label={"Approved": "success", "Pending": "warning", "Rejected": "danger"})
    def display_status(self, obj):
        return obj.status

@admin.register(MealPlan)
class MealPlanAdmin(BaseAdmin):
    list_display = ["name", "day_of_week", "meal_date", "open_date", "close_date"]
    inlines = [MealOptionInline]

    @display(description="Ugedag")
    def day_of_week(self, obj):
        return obj.meal_date.strftime("%A")

# Registration for remaining models using the new BaseAdmin features
@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    list_display = ["name", "description", "last_updated"]
