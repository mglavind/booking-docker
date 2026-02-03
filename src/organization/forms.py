from django import forms
from . import models
from django.utils import timezone

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import time
from django.forms import TextInput


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = models.Volunteer  # Use your custom Volunteer model here
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'



class TeamForm(forms.ModelForm):
    class Meta:
        model = models.Team
        fields = [
            "name",
            "short_name",
           # "events",
        ]


class TeamMembershipForm(forms.ModelForm):
    class Meta:
        model = models.TeamMembership
        fields = [
            "member",
            "team",
            "role",
        ]

    def __init__(self, *args, **kwargs):
        super(TeamMembershipForm, self).__init__(*args, **kwargs)
        self.fields["team"].queryset = models.Team.objects.all()
        self.fields["member"].queryset = models.Volunteer.objects.all()



class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = [
            "name",
            "is_active",
            "start_date",
            "end_date",
            "deadline_sjak",
            "deadline_teknik",
            "deadline_mad",
            "deadline_aktivitetsteam",
            "deadline_foto",
            "deadline_lokaler",
            "deadline_sos",
        ]


class EventMembershipForm(forms.ModelForm):
    class Meta:
        model = models.EventMembership
        fields = [
            "event",
            "volunteer",
        ]

    def __init__(self, *args, **kwargs):
        super(EventMembershipForm, self).__init__(*args, **kwargs)
        self.fields["event"].queryset = models.Event.objects.all()
        self.fields["volunteer"].queryset = models.Volunteer.objects.all()

class TeamEventMembershipForm(forms.ModelForm):
    class Meta:
        model = models.TeamEventMembership
        fields = [
            "event",
            "team",
        ]

    def __init__(self, *args, **kwargs):
        super(TeamEventMembershipForm, self).__init__(*args, **kwargs)
        self.fields["event"].queryset = models.Event.objects.all()
        self.fields["team"].queryset = models.Team.objects.all()



class VolunteerForm(forms.ModelForm):
    class Meta:
        model = models.Volunteer
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
        ]


class KeyForm(forms.ModelForm):
    class Meta:
        model = models.Key
        fields = [
            "number",
            "name", 
            "description", 
            "current_user"] 
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
                }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly' 
                }),
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'readonly': 'readonly' 
                }),
            'current_user': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'number': 'Nøgle nummer',
            'name': 'Nøgle navn',
            'description': 'Beskrivelse',
            'current_user': 'Udleveret til',
        }

    def __init__(self, *args, **kwargs):
        super(KeyForm, self).__init__(*args, **kwargs)
        self.fields["current_user"].queryset = models.Volunteer.objects.all().order_by('first_name')



class AppointmentForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=TextInput(attrs={"type": "date", "class": "form-control"}),
        label="Start Dato"
    )
    start_time = forms.TimeField(
        widget=TextInput(attrs={"type": "time", "class": "form-control"}),
        label="Start tidspunkt"
    )
    end_date = forms.DateField(
        widget=TextInput(attrs={"type": "date", "class": "form-control"}),
        label="Slut Dato"
    )
    end_time = forms.TimeField(
        widget=TextInput(attrs={"type": "time", "class": "form-control"}),
        label="Slut tidspunkt"
    )
    class Meta:
        model = models.VolunteerAppointment
        fields = [
            'receiver', 
            'start_date', 'start_time', 
            'end_date', 'end_time', 
            'description'
        ]
        

    def __init__(self, *args, user=None, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        
        # 1. Setup Querysets
        # We order by first_name to make the dropdown readable
        self.fields["receiver"].queryset = models.Volunteer.objects.all().order_by("first_name")

        # 2. Intelligent Initial Values (Don't override if instance exists)
        instance = kwargs.get('instance')
        
        if instance and instance.pk:
            # When updating, values come from the database
            pass 
        else:
            # For NEW appointments, find the active or next event
            active_event = models.Event.objects.filter(is_active=True).first()
            if not active_event:
                active_event = models.Event.objects.filter(
                    start_date__gt=timezone.now()
                ).order_by('start_date').first()
            
            if active_event:
                self.fields["start_date"].initial = active_event.start_date
                self.fields["end_date"].initial = active_event.start_date # Default to same day
                self.fields["start_time"].initial = time(12, 0)
                self.fields["end_time"].initial = time(13, 0)

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set default status for new appointments
        if not instance.pk:
            instance.status = "pending"
        
        if commit:
            instance.save()
        return instance