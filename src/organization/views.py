from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
from django.views.decorators.http import require_POST
from django.views import generic
from django.urls import reverse_lazy
from .forms import RegisterUserForm
from . import models
from . import forms
from django.db.models import F, Q
from .models import Team, TeamMembership
from django.db.models import IntegerField
from django.db.models.functions import Cast

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





class EventMembershipListView(LoginRequiredMixin, generic.ListView):
    model = models.EventMembership
    form_class = forms.EventMembershipForm


class EventMembershipCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.EventMembership
    form_class = forms.EventMembershipForm


class EventMembershipDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.EventMembership
    form_class = forms.EventMembershipForm


class EventMembershipUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.EventMembership
    form_class = forms.EventMembershipForm
    pk_url_kwarg = "pk"


class EventMembershipDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.EventMembership
    success_url = reverse_lazy("organization_EventMembership_list")


class EventListView(LoginRequiredMixin, generic.ListView):
    model = models.Event
    form_class = forms.EventForm


class EventCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Event
    form_class = forms.EventForm


class EventDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Event
    form_class = forms.EventForm


class EventUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Event
    form_class = forms.EventForm
    pk_url_kwarg = "pk"


class EventDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Event
    success_url = reverse_lazy("organization_Event_list")


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = models.Team
    form_class = forms.TeamForm


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Team
    form_class = forms.TeamForm


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Team
    form_class = forms.TeamForm


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Team
    form_class = forms.TeamForm
    pk_url_kwarg = "pk"


class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Team
    success_url = reverse_lazy("organization_Team_list")


class TeamMembershipListView(LoginRequiredMixin, generic.ListView):
    model = models.TeamMembership
    form_class = forms.TeamMembershipForm


class TeamMembershipCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.TeamMembership
    form_class = forms.TeamMembershipForm


class TeamMembershipDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.TeamMembership
    form_class = forms.TeamMembershipForm


class TeamMembershipUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.TeamMembership
    form_class = forms.TeamMembershipForm
    pk_url_kwarg = "pk"


class TeamMembershipDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.TeamMembership
    success_url = reverse_lazy("organization_TeamMembership_list")


class VolunteerListView(LoginRequiredMixin, generic.ListView):
    model = models.Volunteer
    context_object_name = 'volunteer_list'

    def get_queryset(self):
        return models.Volunteer.objects.filter(
            is_active=True
        ).prefetch_related(
            'teammembership_set__team'
        ).only(
            'first_name', 'last_name', 'phone', 'email', 'id', 'is_active'
        ).order_by('first_name')


class VolunteerCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Volunteer
    form_class = forms.VolunteerForm


class VolunteerDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Volunteer
    form_class = forms.VolunteerForm
    success_url = reverse_lazy("organization_Volunteer_detail")



class VolunteerUpdateView(UserPassesTestMixin, generic.UpdateView):
    model = models.Volunteer
    fields = ['first_name', 'last_name', 'phone']

    def test_func(self):
        # Only allow the user to edit their own profile
        obj = self.get_object()
        return self.request.user == obj

    def handle_no_permission(self):
        # Redirect them back to their own profile if they try to edit someone else's
        return redirect('volunteer_detail', pk=self.request.user.pk)


class VolunteerDeleteView(generic.DeleteView):
    model = models.Volunteer
    success_url = reverse_lazy("organization_Volunteer_list")

class KeyListView(generic.ListView):
    model = models.Key
    form_class = forms.KeyForm
    context_object_name = "key_list"

    def get_queryset(self):
        return models.Key.objects.annotate(
            number_int=Cast('number', IntegerField())
        ).order_by('number_int')


class KeyCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Key
    form_class = forms.KeyForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Du har ikke tilladelse til at oprette en nøgle.")
            return redirect(reverse_lazy('organization_Key_list'))

class KeyDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Key
    form_class = forms.KeyForm


class KeyUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Key
    form_class = forms.KeyForm
    pk_url_kwarg = "pk"

    def dispatch(self, request, *args, **kwargs):
        # Only allow admins
        if not request.user.is_staff:  # or use is_superuser if you prefer
            messages.error(request, "Du har ikke tilladelse til at ændre denne nøgle.")
            # Redirect back to the previous page, or fallback to a safe URL
            return redirect(request.META.get('HTTP_REFERER', reverse_lazy('organization_Key_list')))
        return super().dispatch(request, *args, **kwargs)

class KeyDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Key
    success_url = reverse_lazy("organization_Key_list")



class VolunteerAppointmentListView(LoginRequiredMixin, generic.ListView):
    model = models.VolunteerAppointment
    context_object_name = 'appointments'

    def get_queryset(self):
        user = self.request.user
        # Filter where user is EITHER the requester OR the receiver
        return models.VolunteerAppointment.objects.filter(
            Q(requester=user) | Q(receiver=user)
        ).select_related(
            'requester', 'receiver'
        ).order_by('-start_date', '-start_time')
    
    
class VolunteerAppointmentCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.VolunteerAppointment
    form_class = forms.AppointmentForm
    success_url = reverse_lazy("organization_VolunteerAppointment_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.requester = self.request.user
        form.instance.status = 'pending'
        return super().form_valid(form)

class VolunteerAppointmentDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.VolunteerAppointment

class VolunteerAppointmentUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.VolunteerAppointment
    form_class = forms.AppointmentForm
    # Fallback redirect if get_absolute_url isn't used
    success_url = reverse_lazy("organization_VolunteerAppointment_list") 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class VolunteerAppointmentDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.VolunteerAppointment
    success_url = reverse_lazy("organization_VolunteerAppointment_list")




@login_required
@require_POST
def appointment_status_update(request, pk, new_status):
    # Only the receiver should be able to trigger this
    appointment = get_object_or_404(models.VolunteerAppointment, pk=pk, receiver=request.user)
    if new_status in ['accepted', 'rejected', 'pending']:
        appointment.status = new_status
        appointment.save()
    return redirect('organization_VolunteerAppointment_detail', pk=pk)