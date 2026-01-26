from typing import List
import csv
from datetime import date

from django.contrib import admin, messages
from django.utils.translation import ngettext
from django.contrib.auth.models import Group
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.urls.resolvers import URLPattern
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Unfold Imports
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm

# Import-Export Integration
from import_export.admin import ImportExportModelAdmin
from import_export import resources

# Simple History
from simple_history.admin import SimpleHistoryAdmin

# Local Models
from .models import Volunteer, Team, TeamMembership, TeamEventMembership, EventMembership, Event, Key
from . import models

# --- Import/Export Resources ---

class VolunteerResource(resources.ModelResource):
    class Meta:
        model = Volunteer
        fields = ('first_name', 'last_name', 'username', 'email', 'phone', 'is_active')
        export_order = ('first_name', 'last_name', 'username', 'email', 'phone', 'is_active')

# --- Inlines (Unfold style) ---

class TeamEventMembershipInline(TabularInline):
    model = TeamEventMembership
    extra = 1

class EventMembershipInline(TabularInline):
    model = EventMembership
    extra = 1

class TeamMembershipInline(TabularInline):
    model = TeamMembership
    extra = 1

# --- Admin Classes ---

@admin.register(Team)
class TeamAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["id", "name", "short_name", "last_updated", "created"]
    readonly_fields = ["last_updated", "created"]

@admin.register(TeamMembership)
class TeamMembershipAdmin(ModelAdmin):
    list_display = ["member", "team", "role", "last_updated", "created"]
    readonly_fields = ["last_updated", "created"]

@admin.register(Event)
class EventAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["id", "name", "start_date", "end_date", "is_active", "last_updated", "created"]
    readonly_fields = ["id", "last_updated", "created"]

@admin.register(EventMembership)
class EventMembershipAdmin(ModelAdmin):
    list_display = ["volunteer", "event", "last_updated", "created"]
    readonly_fields = ["last_updated", "created"]

@admin.register(TeamEventMembership)
class TeamEventMembershipAdmin(ModelAdmin):
    list_display = ["team", "last_updated", "created"]
    readonly_fields = ["last_updated", "created"]

@admin.register(Key)
class KeyAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ["number", "name", "current_user", "description"]
    readonly_fields = ["last_updated"]

# --- Volunteer Admin (Unfold + Import/Export + Simple History) ---

@admin.register(Volunteer)
class VolunteerAdmin(SimpleHistoryAdmin, ModelAdmin, ImportExportModelAdmin):
    # Resource for django-import-export
    resource_classes = [VolunteerResource]
    
    # Unfold specific Import/Export forms
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    inlines = [EventMembershipInline, TeamMembershipInline]
    
    list_display = [
        "first_name",
        "last_name",
        "username",
        "display_events",
        "display_teams",
        "is_active",
        "created",
    ]
    
    search_fields = ['first_name', 'last_name', 'email', 'username']
    list_filter = ['is_active', 'events', 'teams', 'last_updated']
    readonly_fields = ["created", "last_updated"]
    ordering = ['first_name', 'last_name']

    actions = [
        "send_email_action",
        "deactivate_volunteers",
        "activate_volunteers",
        "create_event_membership",
        "assign_to_aktivitetsteam_group"
    ]

    def display_events(self, obj):
        return ", ".join([event.name for event in obj.events.all()])
    display_events.short_description = "Events"

    def display_teams(self, obj):
        return ", ".join([team.name for team in obj.teams.all()])
    display_teams.short_description = "Teams"

    # --- Unfold Decorated Actions ---

    @action(description="Assign to AktivitetstTeamBookingTildeling group")
    def assign_to_aktivitetsteam_group(self, request, queryset):
        group, _ = Group.objects.get_or_create(name="AktivitetstTeamBookingTildeling")
        for volunteer in queryset:
            volunteer.groups.add(group)
        self.message_user(request, "Group assignment complete.")

    @action(description="Send 'Hjælp til at komme igang' email")
    def send_email_action(self, request, queryset):
        email_template = "organization/reset_password_guide_email.html"
        for volunteer in queryset:
            subject = "Velkommen til Seniorkursus Slettens booking system"
            context = {'volunteer': volunteer, 'first_team': volunteer.teams.first()}
            message = render_to_string(email_template, context)
            send_mail(subject, strip_tags(message), 'seniorkursussletten@gmail.com', [volunteer.email], html_message=message)
        self.message_user(request, f"Emails sent to {queryset.count()} volunteers.")

    @action(description="Deactivate selected volunteers")
    def deactivate_volunteers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Volunteers deactivated.", messages.SUCCESS)

    @action(description="Activate selected volunteers")
    def activate_volunteers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Volunteers activated.", messages.SUCCESS)

    @action(description="Add selected to the next upcoming event")
    def create_event_membership(self, request, queryset):
        next_event = Event.objects.filter(start_date__gte=date.today()).order_by('start_date').first()
        if next_event:
            for volunteer in queryset:
                EventMembership.objects.get_or_create(volunteer=volunteer, event=next_event)
            self.message_user(request, f'Added to event: {next_event}', messages.SUCCESS)
        else:
            self.message_user(request, "No upcoming events found.", messages.ERROR)