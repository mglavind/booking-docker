from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.http import Http404
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse_lazy
from .forms import RegisterUserForm
from . import models
from . import forms
from django.db.models import F
from .models import Team, TeamMembership

User = get_user_model()



@login_required
def home(request):
    return render(request, 'index.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username'].lower()  # Convert to lowercase
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            LogEntry.objects.log_action(
                user_id=user.pk,
                content_type_id=ContentType.objects.get_for_model(user).pk,
                object_id=user.pk,
                object_repr=str(user),
                action_flag=ADDITION,
                change_message=f'User {user.username} logged in at {now()}.',
            )
            return redirect('index')
        else:
            messages.error(request, "There was an error logging in. Please try again.")
            return redirect('login_user')
    else:
        return render(request, 'organization/login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ("You Were Logged Out!"))
	return redirect('home')


def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['username'].lower()  # Convert to lowercase
            password = form.cleaned_data['password1']

            User = get_user_model()  # Get the custom user model
            
            # Create a new user instance and set is_active to False
            new_user = User.objects.create_user(username=new_username, password=password, is_active=False)

            # Check if the team "Unassigned users" exists
            try:
                new_users_team = Team.objects.get(name="Unassigned users")
            except Team.DoesNotExist:
                # Handle the case when the team doesn't exist
                pass
            else:
                # Create a TeamMembership for the new user
                TeamMembership.objects.create(team=new_users_team, member=new_user)

            messages.success(request, "Registration Successful!")
            return redirect('home')
    else:
        form = RegisterUserForm()

    return render(request, 'organization/register_user.html', {
        'form': form,
    })



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'organization/password_reset.html'
    email_template_name = 'organization/password_reset_email.html'
    subject_template_name = 'organization/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')





class EventMembershipListView(generic.ListView):
    model = models.EventMembership
    form_class = forms.EventMembershipForm


class EventMembershipCreateView(generic.CreateView):
    model = models.EventMembership
    form_class = forms.EventMembershipForm


class EventMembershipDetailView(generic.DetailView):
    model = models.EventMembership
    form_class = forms.EventMembershipForm


class EventMembershipUpdateView(generic.UpdateView):
    model = models.EventMembership
    form_class = forms.EventMembershipForm
    pk_url_kwarg = "pk"


class EventMembershipDeleteView(generic.DeleteView):
    model = models.EventMembership
    success_url = reverse_lazy("organization_EventMembership_list")


class EventListView(generic.ListView):
    model = models.Event
    form_class = forms.EventForm


class EventCreateView(generic.CreateView):
    model = models.Event
    form_class = forms.EventForm


class EventDetailView(generic.DetailView):
    model = models.Event
    form_class = forms.EventForm


class EventUpdateView(generic.UpdateView):
    model = models.Event
    form_class = forms.EventForm
    pk_url_kwarg = "pk"


class EventDeleteView(generic.DeleteView):
    model = models.Event
    success_url = reverse_lazy("organization_Event_list")


class TeamListView(generic.ListView):
    model = models.Team
    form_class = forms.TeamForm


class TeamCreateView(generic.CreateView):
    model = models.Team
    form_class = forms.TeamForm


class TeamDetailView(generic.DetailView):
    model = models.Team
    form_class = forms.TeamForm


class TeamUpdateView(generic.UpdateView):
    model = models.Team
    form_class = forms.TeamForm
    pk_url_kwarg = "pk"


class TeamDeleteView(generic.DeleteView):
    model = models.Team
    success_url = reverse_lazy("organization_Team_list")


class TeamMembershipListView(generic.ListView):
    model = models.TeamMembership
    form_class = forms.TeamMembershipForm


class TeamMembershipCreateView(generic.CreateView):
    model = models.TeamMembership
    form_class = forms.TeamMembershipForm


class TeamMembershipDetailView(generic.DetailView):
    model = models.TeamMembership
    form_class = forms.TeamMembershipForm


class TeamMembershipUpdateView(generic.UpdateView):
    model = models.TeamMembership
    form_class = forms.TeamMembershipForm
    pk_url_kwarg = "pk"


class TeamMembershipDeleteView(generic.DeleteView):
    model = models.TeamMembership
    success_url = reverse_lazy("organization_TeamMembership_list")


class VolunteerListView(generic.ListView):
    model = models.Volunteer
    form_class = forms.VolunteerForm
    template_name = 'volunteer_list.html'  # Change this to the path of your template

    def get_queryset(self):
        # Fetch all volunteers and annotate them with the team name they are members of
        queryset = models.Volunteer.objects.annotate(team_name=F('teammembership__team__name'))

        # Sort volunteers based on the team name
        volunteers_sorted = queryset.order_by('first_name')

        return volunteers_sorted.values('team_name', 'first_name', 'last_name', 'phone', 'email')


class VolunteerCreateView(generic.CreateView):
    model = models.Volunteer
    form_class = forms.VolunteerForm


class VolunteerDetailView(generic.DetailView):
    model = models.Volunteer
    form_class = forms.VolunteerForm
    success_url = reverse_lazy("organization_Volunteer_detail")


class VolunteerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Volunteer
    form_class = forms.VolunteerForm
    pk_url_kwarg = "pk"
    

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.request.user.pk)  # Filter by logged-in user's pk

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj != self.request.user:  # Make sure the user is editing their own profile
            raise Http404

        return super().dispatch(request, *args, **kwargs)


class VolunteerDeleteView(generic.DeleteView):
    model = models.Volunteer
    success_url = reverse_lazy("organization_Volunteer_list")

