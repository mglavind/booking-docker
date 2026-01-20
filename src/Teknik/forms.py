from django import forms
from django.forms.widgets import SelectDateWidget
from organization.models import Team, TeamMembership, Volunteer, Event
from Teknik.models import TeknikItem, TeknikType, TeknikBooking
from django.contrib.auth.models import Group
from . import models
from django.forms import BaseFormSet, TextInput, formset_factory
from django.utils import timezone
from datetime import time

class TeknikBookingForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=TextInput(attrs={"type": "date"}),
        initial=Event.objects.filter(is_active=True).first().start_date,
        label="Afhentning Dato:"
    )
    start_time = forms.TimeField(
        widget=TextInput(attrs={"type": "time"}),
        initial=Event.objects.filter(is_active=True).first().start_date,
        label="Afhentning tidspunk:"
    )
    end_date = forms.DateField(
        widget=TextInput(attrs={"type": "date"}),
        initial=Event.objects.filter(is_active=True).first().end_date,
        label="Retur dato:"
    )
    end_time = forms.TimeField(
        widget=TextInput(attrs={"type": "time"}),
        initial=Event.objects.filter(is_active=True).first().end_date,
        label="Retur tidspunkt:"
    )
    

    class Meta:
        model = models.TeknikBooking
        
        fields = [
            "quantity",
            "team",
            "item",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "team_contact",
            "remarks",
            "delivery_needed",
            "assistance_needed",
            "latitude",
            "longitude",
            "address",

        ]
        widgets = {
            "item": forms.Select(attrs={"class": "form-select"}),
            "team": forms.Select(attrs={"class": "form-select"}),
            "team_contact": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "remarks": forms.Textarea(attrs={"class": "form-control"}),
            "delivery_needed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "assistance_needed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "latitude": forms.TextInput(attrs={"class": "form-control"}),
            "longitude": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),   
        }
        labels = {
            "quantity": "Antal",
            "team": "Team",
            "item": "Teknik ting",
            "team_contact": "Kontaktperson",
            "remarks": "Bemærkninger",
            "delivery_needed": "Levering nødvendig",
            "assistance_needed": "Vi ønsker assistance",
            "latitude" : "latitude",
            "longitude": "longitude",
            "address": "Addresse",
        }


    def save(self, commit=True):
        print("TeknikBookingForm.save() begin")
        instance = super().save(commit=False)
        print("instance loaded")
        instance.status = "Pending"
        print("Instance set to pending")
        if commit:
            print("Connet exists")
            instance.save()
            print("instance saved")
        return instance

    def __init__(self, *args, user=None, **kwargs):
        super(TeknikBookingForm, self).__init__(*args, **kwargs)
        self.fields["team"].queryset = Team.objects.all().order_by("name")
        self.fields["item"].queryset = TeknikItem.objects.all().order_by("name")
        
        if user:
            try:
                team_membership = TeamMembership.objects.get(member=user)
                self.fields["team"].initial = team_membership.team
                self.fields["team_contact"].queryset = Volunteer.objects.filter(
                    teammembership__team=team_membership.team
                )
            except TeamMembership.DoesNotExist:
                pass
            
            self.fields["team_contact"].initial = user
# Function to get the next event
        def get_next_event():
            now = timezone.now()
            next_event = Event.objects.filter(start_date__gt=now).order_by('start_date').first()
            return next_event
        
        # Set initial values from instance
        instance = kwargs.get('instance')
        if instance:
            self.fields["quantity"].initial = instance.quantity
            self.fields["start_date"].initial = instance.start_date
            self.fields["end_date"].initial = instance.end_date
            self.fields["start_time"].initial = instance.start_time
            self.fields["end_time"].initial = instance.end_time
        else:
            # Use the next event's start date if no instance or new instance
            next_event = get_next_event()
            if next_event:
                self.fields["start_date"].initial = next_event.start_date.strftime('%Y-%m-%d')
                self.fields["start_time"].initial = time(8, 0)  # Set default time to 08:00 AM
                self.fields["end_time"].initial = time(8, 0)  # Set default time to 08:00 AM
                self.fields["end_date"].initial = next_event.end_date.strftime('%Y-%m-%d')
                
        
            # Add other fields similarly



class TeknikItemForm(forms.ModelForm):
    class Meta:
        model = models.TeknikItem
        fields = [
            "name",
            "description",
        ]

    def __init__(self, *args, **kwargs):
        super(TeknikItemForm, self).__init__(*args, **kwargs)



class TeknikTypeForm(forms.ModelForm):
    class Meta:
        model = models.TeknikType
        fields = [
            "name",
        ]
