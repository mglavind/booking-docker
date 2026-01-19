from typing import List

from django.contrib import admin, messages
from django.utils.translation import ngettext
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.urls import path
from django.shortcuts import render
from organization.models import Team, TeamMembership, TeamEventMembership, EventMembership, Event
from django.db.models import Min
from datetime import date
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.urls.resolvers import URLPattern
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter

from unfold.admin import ModelAdmin

from .models import Volunteer
import random
from datetime import datetime
import csv

from . import models


class TeamAdminForm(forms.ModelForm):
    class Meta:
        model = models.Team
        fields = "__all__"


class TeamEventMembershipInline(admin.TabularInline):
    model = TeamEventMembership
    extra = 1


class TeamAdmin(ModelAdmin):
    form = TeamAdminForm
    list_display = [
        "id",
        "name",
        "short_name",
        "last_updated",
        "created",
    ]
    readonly_fields = [
        "last_updated",
        "created",
    ]


class TeamMembershipAdminForm(forms.ModelForm):
    class Meta:
        model = models.TeamMembership
        fields = "__all__"


class TeamMembershipAdmin(ModelAdmin):
    form = TeamMembershipAdminForm
    list_display = [
        "member",
        "team",
        "role",
        "last_updated",
        "created",
    ]
    readonly_fields = [
        "last_updated",
        "created",
    ]


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = "__all__"


class EventAdmin(ModelAdmin):
    form = EventAdminForm
    list_display = [
        "id",
        "name",
        "start_date",
        "end_date",  
        "is_active",  
        "last_updated",
        "created",
    ]
    readonly_fields = [
        "id",
        "last_updated",
        "created",
    ]


class EventMembershipAdminForm(forms.ModelForm):
    class Meta:
        model = models.EventMembership
        fields = "__all__"


class EventMembershipAdmin(ModelAdmin):
    form = EventMembershipAdminForm
    list_display = [
        "volunteer",
        "event",
        "last_updated",
        "created",
    ]
    readonly_fields = [
        "last_updated",
        "created",
    ]


class TeamEventMembershipAdminForm(forms.ModelForm):
    class Meta:
        model = models.TeamEventMembership
        fields = "__all__"


class TeamEventMembershipAdmin(ModelAdmin):
    form = TeamEventMembershipAdminForm
    list_display = [
        "team",
        "last_updated",
        "created",
    ]
    readonly_fields = [
        "last_updated",
        "created",
    ]


class VolunteerAdminForm(forms.ModelForm):
    class Meta:
        model = models.Volunteer
        fields = "__all__"


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class EventMembershipInline(admin.TabularInline):
    model = EventMembership
    extra = 1


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 1


class VolunteerAdmin(ModelAdmin):
    form = VolunteerAdminForm
    inlines = [EventMembershipInline, TeamMembershipInline]
    list_display = [
        "first_name",
        "last_name",
        "username",
        "display_events",
        "display_teams",
        "created",
        "last_updated",
    ]
    readonly_fields = [
        "created",
        "last_updated",
    ]
    actions = [
        "export_to_csv",
        "send_email_action",
        "deactivate_volunteers",
        "activate_volunteers",
        "create_event_membership",
        "assign_to_aktivitetsteam_group"
    ]
    search_fields = ['first_name', 'last_name', 'email', 'username'] 
    list_filter = (
        ('last_updated', DropdownFilter),
        ('events', RelatedDropdownFilter),
        ('teams', RelatedDropdownFilter),
    )
    ordering = ['first_name', 'last_name']

    def display_events(self, obj):
        return ", ".join([event.name for event in obj.events.all()])

    def display_teams(self, obj):
        return ", ".join([team.name for team in obj.teams.all()])

    # CSV export
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="volunteers.csv"'
        response.write(u'\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Username', 'Email', 'Phone', 'events'])

        for volunteer in queryset:
            writer.writerow([volunteer.first_name, volunteer.last_name, volunteer.username, volunteer.email, volunteer.phone,  volunteer.events])
        return response
    export_to_csv.short_description = "Export selected volunteers to CSV"

    # CSV upload
    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv)]
        return new_urls + urls

    def upload_csv(self, request):
        # keep your CSV upload logic here unchanged
        ...

    # Assign to group
    def assign_to_aktivitetsteam_group(self, request, queryset):
        group, created = Group.objects.get_or_create(name="AktivitetstTeamBookingTildeling")
        for volunteer in queryset:
            volunteer.groups.add(group)
        self.message_user(request, f"Selected volunteers have been assigned to the group 'AktivitetstTeamBookingTildeling'.")
    assign_to_aktivitetsteam_group.short_description = "Assign selected volunteers to AktivitetstTeamBookingTildeling group"

    # Send email action
    def send_email_action(self, request, queryset):
        email_template = "organization/reset_password_guide_email.html"
        for volunteer in queryset:
            subject = "Velkommen til Seniorkursus Slettens booking system"
            first_team = volunteer.teams.first()
            context = {'volunteer': volunteer, 'first_team': first_team}
            message = render_to_string(email_template, context)
            plain_message = strip_tags(message)
            send_mail(subject, plain_message, 'seniorkursussletten@gmail.com', [volunteer.email], html_message=message)
        self.message_user(request, f"Emails sent to {queryset.count()} volunteers.")
    send_email_action.short_description = "Send hjælp til at komme igang email til volunteers"

    # Activate/deactivate
    def deactivate_volunteers(self, request, queryset):
        count = queryset.count()
        for volunteer in queryset:
            volunteer.is_active = False
            volunteer.save()
        self.message_user(
            request,
            ngettext(
                '%d volunteer was successfully deactivated.',
                '%d volunteers were successfully deactivated.',
                count,
            ) % count,
            messages.SUCCESS,
        )
    deactivate_volunteers.short_description = "Deactivate selected volunteers"

    def activate_volunteers(self, request, queryset):
        count = queryset.count()
        for volunteer in queryset:
            volunteer.is_active = True
            volunteer.save()
        self.message_user(
            request,
            ngettext(
                '%d volunteer was successfully activated.',
                '%d volunteers were successfully activated.',
                count,
            ) % count,
            messages.SUCCESS,
        )
    activate_volunteers.short_description = "Activate selected volunteers"

    # Add to next event
    def create_event_membership(self, request, queryset):
        next_event = Event.objects.filter(start_date__gte=date.today()).order_by('start_date').first()
        for volunteer in queryset:
            EventMembership.objects.create(volunteer=volunteer, event=next_event)
        self.message_user(request, f'Event Memberships created for selected volunteers with the next upcoming event: {next_event}', level='success')
    create_event_membership.short_description = "Add selected to the next event"

class KeyAdminForm(forms.ModelForm):

    class Meta:
        model = models.Key
        fields = "__all__"


class KeyAdmin(admin.ModelAdmin):
    form = KeyAdminForm
    list_display = [
        "number",
        "name",
        "current_user",
        "description",
    ]
    readonly_fields = [
        "last_updated",
    ]




# Register all models
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.TeamMembership, TeamMembershipAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.EventMembership, EventMembershipAdmin)
admin.site.register(models.Volunteer, VolunteerAdmin)
admin.site.register(models.TeamEventMembership, TeamEventMembershipAdmin)
