from django.db import models
from django.utils import timezone

# Create your models here.
class AktivitetsTeamItem(models.Model):

    # Fields
    description = models.TextField(max_length=2000)
    short_description = models.TextField(max_length=200)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    name = models.CharField(max_length=100)

    class Meta:
        pass

    def __str__(self):
        return str(self.name)
    

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True, max_length=2000)  # Set an appropriate max length
    start_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)