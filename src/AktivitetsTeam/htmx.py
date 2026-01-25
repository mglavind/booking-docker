from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import HttpResponse
from django.template import Template, RequestContext
from django.template.response import TemplateResponse

from . import models
from . import forms


class HTMXAktivitetsTeamItemListView(generic.ListView):
    model = models.AktivitetsTeamItem
    form_class = forms.AktivitetsTeamItemForm
    
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request,'htmx/list.html', context)


class HTMXAktivitetsTeamItemCreateView(generic.CreateView):
    model = models.AktivitetsTeamItem
    form_class = forms.AktivitetsTeamItemForm
    
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXAktivitetsTeamItemDeleteView(generic.DeleteView):
    model = models.AktivitetsTeamItem
    success_url = reverse_lazy("AktivitetsTeam_AktivitetsTeamItem_htmx_list")
    
    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()


class HTMXAktivitetsTeamBookingListView(generic.ListView):
    model = models.AktivitetsTeamBooking
    form_class = forms.AktivitetsTeamBookingForm
    
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "objects": self.get_queryset()
        }
        return TemplateResponse(request,'htmx/list.html', context)


class HTMXAktivitetsTeamBookingCreateView(generic.CreateView):
    model = models.AktivitetsTeamBooking
    form_class = forms.AktivitetsTeamBookingForm
    
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(request, 'htmx/form.html', context)

    def form_valid(self, form):
        super().form_valid(form)
        context = {
            "model_id": self.model._meta.verbose_name_raw,
            "object": self.object,
            "form": form
        }
        return TemplateResponse(self.request, 'htmx/create.html', context)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = {
            "create_url": self.model.get_htmx_create_url(),
            "form": self.get_form()
        }
        return TemplateResponse(self.request, 'htmx/form.html', context)


class HTMXAktivitetsTeamBookingDeleteView(generic.DeleteView):
    model = models.AktivitetsTeamBooking
    success_url = reverse_lazy("AktivitetsTeam_AktivitetsTeamBooking_htmx_list")
    
    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse()
