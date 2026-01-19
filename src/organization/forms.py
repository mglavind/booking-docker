from django import forms
from organization.models import Team
from organization.models import Event
from .models import Volunteer
from . import models

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Volunteer  # Use your custom Volunteer model here
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
        self.fields["team"].queryset = Team.objects.all()
        self.fields["member"].queryset = Volunteer.objects.all()



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
        self.fields["event"].queryset = Event.objects.all()
        self.fields["volunteer"].queryset = Volunteer.objects.all()

class TeamEventMembershipForm(forms.ModelForm):
    class Meta:
        model = models.TeamEventMembership
        fields = [
            "event",
            "team",
        ]

    def __init__(self, *args, **kwargs):
        super(TeamEventMembershipForm, self).__init__(*args, **kwargs)
        self.fields["event"].queryset = Event.objects.all()
        self.fields["team"].queryset = Team.objects.all()



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
            "current_user"]  # add/remove as needed
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'  # Make the field read-only
                }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'  # Make the field read-only
                }),
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'readonly': 'readonly'  # Make the field read-only
                }),
            'current_user': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'number': 'Nøgle nummer',
            'name': 'Nøgle navn',
            'description': 'Beskrivelse',
            'current_user': 'Nuværende bruger',
        }

    def __init__(self, *args, **kwargs):
        super(KeyForm, self).__init__(*args, **kwargs)
        self.fields["current_user"].queryset = Volunteer.objects.all().order_by('first_name')
