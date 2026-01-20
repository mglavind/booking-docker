from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from . import models
from . import forms
from django.contrib import messages
from organization.models import EventMembership, Event
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test

class FotoItemListView(LoginRequiredMixin,generic.ListView):
    model = models.FotoItem
    form_class = forms.FotoItemForm
    context_object_name = 'object_list'

    def get_queryset(self):
        queryset = models.FotoItem.objects.all().order_by('name')  # Order by the 'name' field
        return queryset



class FotoItemCreateView(LoginRequiredMixin,generic.CreateView):
    model = models.FotoItem
    form_class = forms.FotoItemForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        event = Event.objects.filter(is_active=True).first()
        self.item_id = kwargs.get('item_id')

        if event and event.deadline_aktivitetsteam < timezone.now().date():
            messages.error(request, 'Deadline for booking overskredet')
            return redirect('AktivitetsTeam_AktivitetsTeamBooking_list')  # replace with the name of your list view url
        return super().dispatch(request, *args, **kwargs)


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        print(self.request.user)
        return kwargs




class FotoItemDetailView(generic.DetailView):
    model = models.FotoItem
    form_class = forms.FotoItemForm


class FotoItemUpdateView(generic.UpdateView):
    model = models.FotoItem
    form_class = forms.FotoItemForm
    pk_url_kwarg = "pk"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        event = Event.objects.filter(is_active=True).first()
        if event and event.deadline_foto < timezone.now().date():
            messages.error(request, 'Deadline for booking overskredet')
            return redirect('Foto_FotoBooking_list')  # replace with the name of your list view url
        return super().dispatch(request, *args, **kwargs)


class FotoItemDeleteView(generic.DeleteView):
    model = models.FotoItem
    success_url = reverse_lazy("Foto_FotoItem_list")

@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_booking(request, pk):
    booking = get_object_or_404(models.FotoBooking, pk=pk)
    booking.status = 'Approved'
    booking.save()
    next_url = request.GET.get('next', 'Foto_FotoBooking_list')
    return redirect(next_url)

@login_required
@user_passes_test(lambda u: u.is_staff)
def reject_booking(request, pk):
    booking = get_object_or_404(models.FotoBooking, pk=pk)
    booking.status = 'Rejected'
    booking.save()
    next_url = request.GET.get('next', 'Foto_FotoBooking_list')
    return redirect(next_url)


class FotoBookingListView(LoginRequiredMixin, generic.ListView):
    model = models.FotoBooking
    form_class = forms.FotoBookingForm


class FotoBookingCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.FotoBooking
    form_class = forms.FotoBookingForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        event = Event.objects.filter(is_active=True).first()
        self.item_id = kwargs.get('item_id')

        if event and event.deadline_aktivitetsteam < timezone.now().date():
            messages.error(request, 'Deadline for booking overskredet')
            return redirect('AktivitetsTeam_AktivitetsTeamBooking_list')  # replace with the name of your list view url
        return super().dispatch(request, *args, **kwargs)


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        print(self.request.user)
        return kwargs


class FotoBookingDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.FotoBooking
    form_class = forms.FotoBookingForm


class FotoBookingUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.FotoBooking
    form_class = forms.FotoBookingForm
    pk_url_kwarg = "pk"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        event = Event.objects.filter(is_active=True).first()
        if event and event.deadline_foto < timezone.now().date():
            messages.error(request, 'Deadline for booking overskredet')
            return redirect('Foto_FotoBooking_list')  # replace with the name of your list view url
        return super().dispatch(request, *args, **kwargs)


class FotoBookingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = models.FotoBooking
    success_url = reverse_lazy("Foto_FotoBooking_list")
