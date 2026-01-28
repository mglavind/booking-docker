from django import forms
from django.forms import TextInput
from django.utils import timezone
from datetime import time
from . import models
from Sjak.models import SjakItem, SjakItemType, SjakItemLocation
from organization.models import Team, TeamMembership, Volunteer, Event
from utils.image_utils import process_image

class SjakBookingForm(forms.ModelForm): 
    # Defined without initial values to prevent crashes on startup
    start = forms.DateField(
        widget=TextInput(attrs={"type": "date", "class": "form-control"}),
        label="Start Dato"
    )
    start_time = forms.TimeField(
        widget=TextInput(attrs={"type": "time", "class": "form-control"}),
        label="Start tidspunkt"
    )
    end = forms.DateField(
        widget=TextInput(attrs={"type": "date", "class": "form-control"}),
        label="Slut Dato"
    )
    end_time = forms.TimeField(
        widget=TextInput(attrs={"type": "time", "class": "form-control"}),
        label="Slut tidspunkt"
    )

    class Meta:
        model = models.SjakBooking
        fields = [
            "start", "start_time", "end", "end_time",
            "team_contact", "item", "team", "remarks", "quantity",
        ]
        labels = {
            "item": "Vælg en ting",       # Changed from "Sjak ting"
            "quantity": "Antal",   # Changed from "Antal"
            "team": "Team",
            "team_contact": "Kontaktperson",
            "start": "Udlånsdato",
            "end": "Afleveringsdato",
            "remarks": "Bemærkninger til Sjak",
        }
        widgets = {
            # Add 'tom-select' class here
            "item": forms.Select(attrs={"class": "tom-select", "placeholder": "Søg efter ting..."}),
            "team": forms.Select(attrs={"class": "form-select"}),
            "team_contact": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "1", "min": "1"}),
            "remarks": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super(SjakBookingForm, self).__init__(*args, **kwargs)
        
        # 1. Setup Querysets
        self.fields["item"].queryset = SjakItem.objects.all().order_by("name")
        self.fields["team"].queryset = Team.objects.all().order_by("name")
        self.fields["team_contact"].queryset = Volunteer.objects.all().order_by("first_name")
        self.fields["item"].empty_label = "Begynd at skrive for at filtrere listen..."

        # 2. Handle User-specific logic
        if user:
            self.fields["team_contact"].initial = user
            try:
                team_membership = TeamMembership.objects.get(member=user)
                self.fields["team"].initial = team_membership.team
                # Filter contacts to only show people from the same team
                self.fields["team_contact"].queryset = Volunteer.objects.filter(
                    teammembership__team=team_membership.team
                ).order_by("first_name")
            except TeamMembership.DoesNotExist:
                pass

        # 3. Intelligent Initial Values (Don't override if instance exists)
        instance = kwargs.get('instance')
        if instance:
            # When updating, fields are automatically populated by ModelForm.
            # We just ensure the date/time fields match the instance.
            self.fields["start"].initial = instance.start
            self.fields["start_time"].initial = instance.start_time
            self.fields["end"].initial = instance.end
            self.fields["end_time"].initial = instance.end_time
        else:
            # For NEW bookings, find the active or next event
            active_event = Event.objects.filter(is_active=True).first()
            if not active_event:
                active_event = Event.objects.filter(start_date__gt=timezone.now()).order_by('start_date').first()
            
            if active_event:
                self.fields["start"].initial = active_event.start_date
                self.fields["end"].initial = active_event.end_date
                self.fields["start_time"].initial = time(12, 0)
                self.fields["end_time"].initial = time(12, 0)

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set default statuses for new bookings
        if not instance.pk:
            instance.status = "Pending"
            instance.status_internal = "Afventer"
        
        if commit:
            instance.save()
        return instance

class SjakItemForm(forms.ModelForm):
    class Meta:
        model = models.SjakItem
        fields = ["name", "description", "item_type", "location", "quantity_lager", "image"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "item_type": forms.Select(attrs={"class": "form-select"}),
            "location": forms.Select(attrs={"class": "form-select"}),
            "quantity_lager": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Navn",
            "item_type": "Type",
            "location": "Placering",
            "quantity_lager": "Antal på lager",
        }

    def __init__(self, *args, **kwargs):
        super(SjakItemForm, self).__init__(*args, **kwargs)
        self.fields["item_type"].queryset = SjakItemType.objects.all().order_by("name")
        self.fields["location"].queryset = SjakItemLocation.objects.all().order_by("name")

    def save(self, commit=True):
        instance = super().save(commit=False)
        image_field = self.cleaned_data.get('image')
        if image_field:
            new_filename, image_content = process_image(image_field, instance)
            instance.image.save(new_filename, image_content, save=False)
        if commit:
            instance.save()
        return instance

class SjakItemTypeForm(forms.ModelForm):
    class Meta:
        model = models.SjakItemType
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}