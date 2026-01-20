from django import forms
from organization.models import Team
from Foto.models import FotoItem
from organization.models import Team, TeamMembership, Volunteer, Event
from . import models
from django.utils import timezone
from datetime import time

class FotoItemForm(forms.ModelForm):
    class Meta:
        model = models.FotoItem
        fields = [
            "name",
            "description",
        ]



class FotoBookingForm(forms.ModelForm):
    class Meta:
        model = models.FotoBooking
        fields = [
            "item",
            "team",
            "team_contact",
            "remarks",
            "location",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
        ]
        widgets = {
            "item": forms.Select(attrs={"class": "form-select"}),
            "team": forms.Select(attrs={"class": "form-select"}),
            "team_contact": forms.Select(attrs={"class": "form-select"}),
            "remarks": forms.Textarea(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control"}),
            "end_date": forms.DateInput(attrs={"class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control"}),            
        }
        labels = {
            "team": "Team",
            "item": "Foto item",
            "start_date": "Start Dato",
            "start_time": "Start tidspunkt",
            "end_date": "Slut dato",
            "end_time": "Slut tidspunkt",
            "team_contact": "Kontaktperson",
            "remarks": "Bemærkninger",
        }

    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = "Pending"
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, user=None, **kwargs):
        super(FotoBookingForm, self).__init__(*args, **kwargs)
        self.fields["item"].queryset = FotoItem.objects.all()
        self.fields["team"].queryset = Team.objects.all()
        self.fields["team_contact"].queryset = Volunteer.objects.all()
        if user:
            print("A user exists")
            team_membership = TeamMembership.objects.get(member=user)
            self.fields["team"].initial = team_membership.team
            self.fields["team_contact"].queryset = Volunteer.objects.filter(
                teammembership__team=team_membership.team
            )
            self.fields["team_contact"].initial = user
        
        def get_next_event():
            now = timezone.now()
            next_event = Event.objects.filter(start_date__gt=now).order_by('start_date').first()
            return next_event
        
        # Set initial values from instance
        instance = kwargs.get('instance')
        if instance:
            self.fields["start_date"].initial = instance.start_date
            self.fields["end_date"].initial = instance.end_date
            self.fields["start_time"].initial = instance.start_time
            self.fields["end_time"].initial = instance.end_time            
            self.fields["remarks"].initial = instance.remarks
            self.fields["location"].initial = instance.location
        else:
            # Use the next event's start date if no instance or new instance
            next_event = get_next_event()
            if next_event:
                self.fields["start_date"].initial = next_event.start_date.strftime('%Y-%m-%d')
                self.fields["start_time"].initial = time(8, 0)  # Set default time to 08:00 AM
                self.fields["end_time"].initial = time(8, 0)  # Set default time to 08:00 AM
                self.fields["end_date"].initial = next_event.end_date.strftime('%Y-%m-%d')


