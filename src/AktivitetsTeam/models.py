from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator



class AktivitetsTeamItem(models.Model):

    # Fields
    description = models.TextField(max_length=2000)
    short_description = models.TextField(max_length=200)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    youtube_link = models.TextField(max_length=2000)
    description_flow = models.TextField(max_length=200, blank=True)
    description_eksempel = models.TextField(max_length=200, blank=True)
    description_aktiverede = models.TextField(max_length=200, blank=True)
    name = models.CharField(max_length=100)

    image = models.ImageField(upload_to='AktivitetstTeamItem/', blank=True, null=True)


    class Meta:
        pass

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("AktivitetsTeam_AktivitetsTeamItem_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("AktivitetsTeam_AktivitetsTeamItem_update", args=(self.pk,))
    def to_dict(self):
        return {
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            # Add other fields as necessary
        }






class AktivitetsTeamBooking(models.Model):
    # Relationships
    team = models.ForeignKey("organization.Team", on_delete=models.CASCADE)
    item = models.ForeignKey("AktivitetsTeam.AktivitetsTeamItem", on_delete=models.CASCADE)
    team_contact = models.ForeignKey("organization.Volunteer", on_delete=models.CASCADE, related_name='team_contact_bookings')

    # Add Many-to-Many relationship with Volunteer
    assigned_aktivitetsteam = models.ManyToManyField("organization.Volunteer", related_name='Assigned_Aktivitetsteam', blank=True)

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    # Fields
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True, max_length=2000)  # Set an appropriate max length
    start_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    remarks_internal = models.TextField(blank=True, max_length=500)  # Set an appropriate max length
    latitude = models.FloatField(blank=True)
    longitude = models.FloatField(blank=True)
    address = models.CharField(max_length=300, blank=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("AktivitetsTeam_AktivitetsTeamBooking_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("AktivitetsTeam_AktivitetsTeamBooking_update", args=(self.pk,))

    def clean(self):
        if self.start_date and not self.start_time:
            raise ValidationError(_("Start time is required."))
        if self.end_date and not self.end_time:
            raise ValidationError(_("End time is required."))
        if self.start_date and self.start_time and self.end_date and self.end_time:
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(self.start_date, self.start_time)
            )
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(self.end_date, self.end_time)
            )
            if start_datetime >= end_datetime:
                raise ValidationError(_("Start time must be before end time."))
    
    def save(self, *args, **kwargs):
        if self.start_date and self.start_time:
            self.start = timezone.make_aware(
                timezone.datetime.combine(self.start_date, self.start_time),
                timezone.get_default_timezone()
            )
        if self.end_date and self.end_time:
            self.end = timezone.make_aware(
                timezone.datetime.combine(self.end_date, self.end_time),
                timezone.get_default_timezone()
            )
        super().save(*args, **kwargs)
    
    def approve_bookings(self, request, queryset):
        queryset.update(status="Approved")

    approve_bookings.short_description = "Approve selected bookings"

    def reject_bookings(self, request, queryset):
        queryset.update(status="Rejected")

    reject_bookings.short_description = "Reject selected bookings"
    
    def to_dict(self):
        return {
            'name': self.item.name,
            'last_updated': self.last_updated.isoformat(),
            'created': self.created.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            # Add other fields as necessary
        }


