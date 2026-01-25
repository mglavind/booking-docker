from django import forms
from Butikken.models import ButikkenItemType, ButikkenItem, Day, Meal, Option, Recipe
from organization.models import Team, TeamMembership, Volunteer, Event
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import BaseFormSet, TextInput, formset_factory
from . import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone
from datetime import time



from django import forms
from .models import MealPlan, MealOption, TeamMealPlan, MealBooking
from django.contrib.auth.models import User

class MealBookingForm(forms.ModelForm):
    class Meta:
        model = MealBooking
        fields = [
            'team',
            'team_contact',
            'status',
            ]  # Add other fields as necessary
        widgets = {
            "team": forms.Select(attrs={"class": "form-control", "data-error": "Please select a team."}),
            "team_contact": forms.Select(attrs={"class": "form-control", "data-error": "Please select a team contact"}),
            "status": forms.Select(attrs={"class": "form-control", "data-error": "Please select a status."}),
        }
    def __init__(self, *args, user=None, **kwargs):
        super(MealBookingForm, self).__init__(*args, **kwargs)
        self.fields["team_contact"].queryset = Volunteer.objects.all().order_by("first_name")
        self.fields["team"].queryset = Team.objects.all().order_by("name")
        
        self.fields["team_contact"].initial = user
        if user:
            team_membership = TeamMembership.objects.filter(member=user).first()
            
            if team_membership:
                self.fields["team"].initial = team_membership.team
                self.fields["team_contact"].queryset = Volunteer.objects.filter(
                    teammembership__team=team_membership.team
                )
                self.fields["team_contact"].initial = user
            else:
                print(f"Warning: User {user} has no team membership.")

class MealForm(forms.ModelForm):
    class Meta:
        model = models.Meal
        fields = [
            "type",
            "day",
        ]

    def __init__(self, *args, **kwargs):
        super(MealForm, self).__init__(*args, **kwargs)
        self.fields["day"].queryset = Day.objects.all()

class OptionForm(forms.ModelForm):
    class Meta:
        model = models.Option
        fields = [
            "meal",
            "recipe",
        ]

    def __init__(self, *args, **kwargs):
        super(OptionForm, self).__init__(*args, **kwargs)
        self.fields["meal"].queryset = Meal.objects.all()
        self.fields["recipe"].queryset = Recipe.objects.all()



class DayForm(forms.ModelForm):
    class Meta:
        model = models.Day
        fields = [
            "name",
            "date",
        ]


class RecipeForm(forms.ModelForm):
    class Meta:
        model = models.Recipe
        fields = [
            "name",
            "description",
        ]

class ButikkenItemForm(forms.ModelForm):
    class Meta:
        model = models.ButikkenItem
        fields = [
            "description",
            "name",
            "type",
            "content_normal",
            "content_unit",
        ]

    def __init__(self, *args, **kwargs):
        super(ButikkenItemForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = ButikkenItemType.objects.all()

class ButikkenBookingForm(forms.ModelForm):


    # start = forms.DateField(
    #     widget=TextInput(attrs={"type": "date"}),
    #     initial=Event.objects.filter(is_active=True).first().start_date,
    #     label="Afhentning Dato:"
    # )
    # start_time = forms.TimeField(
    #     widget=TextInput(attrs={"type": "time"}),
    #     initial=Event.objects.filter(is_active=True).first().start_date,
    #     label="Afhentning tidspunk:"
    # )
    # date_used = forms.DateField(
    #     widget=TextInput(attrs={"type": "date"}),
    #     initial=Event.objects.filter(is_active=True).first().start_date,
    #     label="Anvendelsesdato"
    # )
    class Meta:
        model = models.ButikkenBooking
        fields =[
            "item",
            "team",
            "team_contact",
            "start",
            "start_time",
            "quantity",
            "unit",
            "for_meal",
            "remarks",
            "date_used",
        ]

        labels = {
            "item": "Vare",
            "team": "Team",
            "team_contact": "Kontaktperson",
            "quantity": "Antal",
            "unit": "Enhed",
            "for_meal": "Måltid",
            "remarks": "Bemærkninger",
            "start": "Afhentning Dato",
            "start_time": "Afhentning Tidspunkt",
            "date_used": "Anvendelsesdato",

        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = "Pending"
        if commit:
            instance.save()
        return instance
    
    def __init__(self, *args, user=None, **kwargs):
        super(ButikkenBookingForm, self).__init__(*args, **kwargs)
        self.fields["item"].queryset = ButikkenItem.objects.all()
        self.fields["team"].queryset = Team.objects.all()
        self.fields["team_contact"].queryset = Volunteer.objects.all()
        
        if user:
            # CHANGE: Use filter().first() instead of .get()
            team_membership = TeamMembership.objects.filter(member=user).first()
            
            if team_membership:
                self.fields["team"].initial = team_membership.team
                self.fields["team_contact"].queryset = Volunteer.objects.filter(
                    teammembership__team=team_membership.team
                )
                self.fields["team_contact"].initial = user
            else:
                print(f"Warning: User {user} has no team membership.")
        
# Function to get the next event
        def get_next_event():
            now = timezone.now()
            next_event = Event.objects.filter(start_date__gt=now).order_by('start_date').first()
            return next_event
        
        # Check if the form is being initialized with an instance
        if self.instance and self.instance.pk:
            # Use the existing value from the instance
            self.fields["start"].initial = self.instance.start.strftime('%Y-%m-%d')
            print(self.instance.start.strftime('%Y-%m-%d'))
        else:
            # Use the next event's start date if no instance or new instance
            next_event = get_next_event()
            if next_event:
                self.fields["start"].initial = next_event.start_date.strftime('%Y-%m-%d')
                self.fields["start_time"].initial = time(8, 0)  # Set default time to 08:00 AM




class OldButikkenBookingForm(forms.ModelForm):
    class Meta:
        model = models.ButikkenBooking
        fields = [
            "remarks",
            "quantity",
            "start",
            "item",
            "team_contact",
            "team",
        ]

        widgets = {
            "item": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "start": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "remarks": forms.Textarea(attrs={"class": "form-control h-25"}),
            "team_contact": forms.Select(attrs={"class": "form-control"}),
            "team": forms.Select(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = "Pending"
        instance.team_contact = self.user
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, user=None, **kwargs):
        print("Initializing ButikkenBookingForm")  # Print to terminal when the method is called
        print("Current user: 0", user) 
        #user = kwargs.pop('user', None)
        self.user = user  # Assign the user argument to the form's user attribute
        print("Current user: 1", user)  # Print to terminal the current user

        super(ButikkenBookingForm, self).__init__(*args, **kwargs)

        if self.user is not None:
            print("Current user: 2", self.user)  # Print to terminal the current user
            team = Team.objects.filter(teammembership__member=self.user).first()
            print("Teams:", team)  # Print to terminal the current user

            self.fields['team_contact'].queryset = Volunteer.objects.filter(teammembership__team=team)
            self.fields['team_contact'].initial = self.user  # Set the default value to be the user object

            self.fields["team"].queryset = Team.objects.filter(teammembership__member=self.user)
            self.fields["team"].initial = team
            
        self.fields["start"].initial = Event.objects.filter(is_active=True).first()
        self.fields["item"].queryset = ButikkenItem.objects.all().order_by("name")
        self.fields["team"].queryset = Team.objects.all().order_by("name")



class ButikkenItemTypeForm(forms.ModelForm):
    class Meta:
        model = models.ButikkenItemType
        fields = [
            "name",
            "description",
        ]


class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = [
            "name",
            "meal_date",
            "open_date",
            "close_date",
        ]

    def __init__(self, *args, **kwargs):
        super(MealPlanForm, self).__init__(*args, **kwargs)

class MealOptionForm(forms.ModelForm):
    class Meta:
        model = MealOption
        fields = [
            "meal_plan",
            "recipe",
        ]

    def __init__(self, *args, **kwargs):
        super(MealOptionForm, self).__init__(*args, **kwargs)
        self.fields["meal_plan"].queryset = MealPlan.objects.all()
        self.fields["recipe"].queryset = Recipe.objects.all()


class TeamMealPlanForm(forms.ModelForm):
    class Meta:
        model = models.TeamMealPlan
        fields = [
            "meal_plan",
            "meal_option",
            "team",
            "team_contact",
        ]
        labels = {
            "meal_plan": "Måltid",
            "meal_option": "Måltidspakke",
            "team": "Team",
            "team_contact": "Kontaktperson",
        }

    def __init__(self, *args, **kwargs):
        meal_plan = kwargs.pop('meal_plan', None)
        user = kwargs.pop('user', None)
        super(TeamMealPlanForm, self).__init__(*args, **kwargs)
        self.fields["meal_plan"].queryset = MealPlan.objects.all()
        self.fields["team"].queryset = Team.objects.all()
        
        if meal_plan:
            self.fields['meal_option'].queryset = MealOption.objects.filter(meal_plan=meal_plan)
        else:
            self.fields['meal_option'].queryset = MealOption.objects.none()
        
        if user:
            # Get the team of the current user
            user_team = models.Team.objects.filter(teammembership__member=user).first()
            if user_team:
                # Filter team_contact to only include volunteers related to the same team
                self.fields['team_contact'].queryset = models.Volunteer.objects.filter(teammembership__team=user_team)
                # Set the default value of team_contact to the current user
                self.fields['team_contact'].initial = user