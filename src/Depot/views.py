from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import DepotItem, DepotBooking
from .forms import DepotItemForm, DepotBookingForm


class DepotItemListView(LoginRequiredMixin, ListView):
    """List all depot items."""
    model = DepotItem
    template_name = 'Depot/depot_item_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        queryset = DepotItem.objects.all()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class DepotItemDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific depot item and its bookings."""
    model = DepotItem
    template_name = 'Depot/depot_item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        
        # Get all bookings for this item
        context['bookings'] = DepotBooking.objects.filter(item=item).select_related('team', 'team_contact')
        
        # Get upcoming bookings (approved only)
        context['upcoming_bookings'] = DepotBooking.objects.filter(
            item=item,
            status='Approved'
        ).order_by('start_date')
        
        return context


class DepotItemCreateView(LoginRequiredMixin, CreateView):
    """Create a new depot item."""
    model = DepotItem
    form_class = DepotItemForm
    template_name = 'Depot/depot_item_form.html'
    success_url = reverse_lazy('Depot_DepotItem_list')


class DepotItemUpdateView(LoginRequiredMixin, UpdateView):
    """Update a depot item."""
    model = DepotItem
    form_class = DepotItemForm
    template_name = 'Depot/depot_item_form.html'
    success_url = reverse_lazy('Depot_DepotItem_list')


class DepotItemDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a depot item."""
    model = DepotItem
    template_name = 'Depot/depot_item_confirm_delete.html'
    success_url = reverse_lazy('Depot_DepotItem_list')


class DepotBookingListView(LoginRequiredMixin, ListView):
    """List all depot bookings with filtering."""
    model = DepotBooking
    template_name = 'Depot/depot_booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        queryset = DepotBooking.objects.select_related('item', 'team', 'team_contact')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by team
        team = self.request.GET.get('team')
        if team:
            queryset = queryset.filter(team__id=team)
        
        # Filter by item
        item = self.request.GET.get('item')
        if item:
            queryset = queryset.filter(item__id=item)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = DepotBooking.STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_team'] = self.request.GET.get('team', '')
        context['selected_item'] = self.request.GET.get('item', '')
        return context


class DepotBookingDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific booking."""
    model = DepotBooking
    template_name = 'Depot/depot_booking_detail.html'
    context_object_name = 'booking'


class DepotBookingCreateView(LoginRequiredMixin, CreateView):
    """Create a new depot booking."""
    model = DepotBooking
    form_class = DepotBookingForm
    template_name = 'Depot/depot_booking_form.html'
    success_url = reverse_lazy('Depot_DepotBooking_list')


class DepotBookingUpdateView(LoginRequiredMixin, UpdateView):
    """Update a depot booking."""
    model = DepotBooking
    form_class = DepotBookingForm
    template_name = 'Depot/depot_booking_form.html'
    success_url = reverse_lazy('Depot_DepotBooking_list')


class DepotBookingDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a depot booking."""
    model = DepotBooking
    template_name = 'Depot/depot_booking_confirm_delete.html'
    success_url = reverse_lazy('Depot_DepotBooking_list')
