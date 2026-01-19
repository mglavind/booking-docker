import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from . import models
from . import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MealBooking, Meal, Day, Option, Recipe, MealPlan, MealOption, TeamMealPlan, MealBooking, TeamMealPlan
from organization.models import Event
import logging

logger = logging.getLogger(__name__)

from .forms import TeamMealPlanForm

from django.contrib import messages
from django.utils import timezone


class ButikkenItemListView(LoginRequiredMixin, generic.ListView):
    model = models.ButikkenItem
    form_class = forms.ButikkenItemForm
    context_object_name = 'object_list'
    ordering = ['name']

    def get_queryset(self):
        queryset = models.ButikkenItem.objects.all().order_by('name')  # Order by the 'name' field
        return queryset
    
    def sort_items(request):
        sort_by = request.GET.get('sort', 'default')  # Default sorting option

        if sort_by == 'name':
            object_list = models.ButikkenItem.objects.all().order_by('name')
        else:
            object_list = models.ButikkenItem.objects.all()

        context = {
            'object_list': object_list,
        }
        return render(request, 'your_template.html', context)


class ButikkenItemCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ButikkenItem
    form_class = forms.ButikkenItemForm


class ButikkenItemDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ButikkenItem
    form_class = forms.ButikkenItemForm


class ButikkenItemUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ButikkenItem
    form_class = forms.ButikkenItemForm
    pk_url_kwarg = "pk"


class ButikkenItemDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.ButikkenItem
    success_url = reverse_lazy("Butikken_ButikkenItem_list")


from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from . import models, forms

class ButikkenBookingListView(LoginRequiredMixin, generic.ListView):
    model = models.ButikkenBooking
    form_class = forms.ButikkenBookingForm
    context_object_name = 'object_list'
    template_name = 'Butikken/butikkenbooking_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return models.ButikkenBooking.objects.select_related(
            'team', 'team_contact', 'item'
        ).order_by('item', 'start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_team_membership = user.teammembership_set.select_related('team').first()
        context['user_team_membership'] = user_team_membership
        return context


class ButikkenBookingCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ButikkenBooking
    form_class = forms.ButikkenBookingForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        event = Event.objects.filter(is_active=True).first()
        if event and event.deadline_mad < timezone.now().date():
            messages.error(request, 'Deadline for booking overskredet')
            return redirect('Butikken_ButikkenBooking_list')  # replace with the name of your list view url
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        butikken_items = models.ButikkenItem.objects.all()
        context['butikken_items'] = butikken_items
        return context
    
def create_butikken_booking(request):
    print("Hello from Def")  # Print to terminal the current user
    if request.method == 'POST':
        form = forms.ButikkenBookingForm(request.POST or None)
        if form.is_valid():
            ButikkenBooking = form.save()
            context = {'booking': ButikkenBooking}
            return render(request, 'Butikken/partials/booking.html', context)
    return render(request, 'Butikken/partials/form.html' , {'form': forms.ButikkenBookingForm()})

class ButikkenBookingDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ButikkenBooking
    form_class = forms.ButikkenBookingForm
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ButikkenBookingUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ButikkenBooking
    form_class = forms.ButikkenBookingForm
    pk_url_kwarg = "pk"
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        event = Event.objects.filter(is_active=True).first()
        if event and event.deadline_mad < timezone.now().date():
            messages.error(request, 'Deadline for booking overskredet')
            return redirect('Butikken_ButikkenBooking_list')  # replace with the name of your list view url
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ButikkenBookingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.ButikkenBooking
    success_url = reverse_lazy("Butikken_ButikkenBooking_list")
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ButikkenItemTypeListView(LoginRequiredMixin, generic.ListView):
    model = models.ButikkenItemType
    form_class = forms.ButikkenItemTypeForm


class ButikkenItemTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ButikkenItemType
    form_class = forms.ButikkenItemTypeForm


class ButikkenItemTypeDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ButikkenItemType
    form_class = forms.ButikkenItemTypeForm


class ButikkenItemTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ButikkenItemType
    form_class = forms.ButikkenItemTypeForm
    pk_url_kwarg = "pk"


class ButikkenItemTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.ButikkenItemType
    success_url = reverse_lazy("Butikken_ButikkenItemType_list")



####### Options

class OptionListView(LoginRequiredMixin, generic.ListView):
    model = models.Option
    form_class = forms.OptionForm


class OptionCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Option
    form_class = forms.OptionForm


class OptionDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Option
    form_class = forms.OptionForm


class OptionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Option
    form_class = forms.OptionForm
    pk_url_kwarg = "pk"


class OptionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Option
    success_url = reverse_lazy("Butikken_Option_list")


###### Meal 



class MealListView(LoginRequiredMixin, generic.ListView):
    model = models.Meal
    form_class = forms.MealForm


class MealCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Meal
    form_class = forms.MealForm


class MealDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Meal
    form_class = forms.MealForm


class MealUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Meal
    form_class = forms.MealForm
    pk_url_kwarg = "pk"


class MealDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Meal
    success_url = reverse_lazy("Butikken_Meal_list")


###### MealBooking


class MealBookingListView(LoginRequiredMixin, generic.ListView):
    model = models.MealBooking
    form_class = forms.MealBookingForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meal_plans'] = models.MealPlan.objects.all()
        return context


class MealBookingCreateView(LoginRequiredMixin, generic.CreateView):
    model = MealBooking
    form_class = forms.MealBookingForm
    template_name = 'Butikken/mealbooking_form.html'
    success_url = reverse_lazy('Butikken_MealBooking_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

class MealBookingUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = MealBooking
    form_class = forms.MealBookingForm
    template_name = 'Butikken/mealbooking_form.html'
    success_url = reverse_lazy('Butikken_MealBooking_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

class MealBookingDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.MealBooking
    form_class = forms.MealBookingForm
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team_meal_plans'] = TeamMealPlan.objects.filter(meal_booking=self.object)
        return context
        

class TeamMealPlanListView(LoginRequiredMixin, generic.ListView):
    model = TeamMealPlan
    form_class = TeamMealPlanForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        print(user)
        if user.is_staff:
            context['TeamMealPlans'] = TeamMealPlan.objects.all().order_by('meal_plan__name')
        else:
            context['TeamMealPlans'] = TeamMealPlan.objects.filter(team__teammembership__member=user).order_by('meal_plan__name')
        return context
        


class TeamMealPlanCreateView(LoginRequiredMixin, generic.CreateView):
    model = TeamMealPlan
    form_class = TeamMealPlanForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TeamMealPlans'] = TeamMealPlan.objects.all()
        return context

class TeamMealPlanDetailView(LoginRequiredMixin, generic.DetailView):
    model = TeamMealPlan
    form_class = TeamMealPlanForm


class TeamMealPlanUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TeamMealPlan
    form_class = TeamMealPlanForm
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("Butikken_TeamMealPlan_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['meal_plan'] = self.object.meal_plan
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meal_plan'] = self.object.meal_plan
        return context


class TeamMealPlanDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TeamMealPlan
    success_url = reverse_lazy("Butikken_TeamMealPlan_list")



#class MealBookingUpdateView(LoginRequiredMixin, generic.UpdateView):
#    model = models.MealBooking
#    form_class = forms.MealBookingForm
#    pk_url_kwarg = "pk"
#    @method_decorator(login_required)
#    def dispatch(self, request, *args, **kwargs):
#        event = Event.objects.filter(is_active=True).first()
#        if event and event.deadline_mad < timezone.now().date():
#            messages.error(request, 'Deadline for booking overskredet')
#            return redirect('Butikken_MealBooking_list')  # replace with the name of your list view url
#        return super().dispatch(request, *args, **kwargs)
#
#    def get_form_kwargs(self):
#        kwargs = super().get_form_kwargs()
#        kwargs['user'] = self.request.user
#        return kwargs


class MealBookingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.MealBooking
    success_url = reverse_lazy("Butikken_MealBooking_list")




class DayListView(LoginRequiredMixin, generic.ListView):
    model = models.Day
    form_class = forms.DayForm


class DayCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Day
    form_class = forms.DayForm


class DayDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Day
    form_class = forms.DayForm


class DayUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Day
    form_class = forms.DayForm
    pk_url_kwarg = "pk"


class DayDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Day
    success_url = reverse_lazy("Butikken_Day_list")


class RecipeListView(LoginRequiredMixin, generic.ListView):
    model = models.Recipe
    form_class = forms.RecipeForm


class RecipeCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Recipe
    form_class = forms.RecipeForm


class RecipeDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.Recipe
    form_class = forms.RecipeForm


class RecipeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Recipe
    form_class = forms.RecipeForm
    pk_url_kwarg = "pk"


class RecipeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.Recipe
    success_url = reverse_lazy("Butikken_Recipe_list")

