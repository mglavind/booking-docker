
from django.contrib import admin
from . import models

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'last_updated')

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'created', 'last_updated')

class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('team', 'member', 'role', 'created', 'last_updated')

admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Volunteer, VolunteerAdmin)
admin.site.register(models.TeamMembership, TeamMembershipAdmin)