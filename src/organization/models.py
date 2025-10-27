from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone





    

class TeamMembership(models.Model):

    # Relationships
    team = models.ForeignKey("organization.Team", on_delete=models.CASCADE, db_index=True)
    member = models.ForeignKey("organization.Volunteer", on_delete=models.CASCADE, db_index=True)

    # Fields
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    role = models.CharField(max_length=30, blank=True)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)
    

    

class Event(models.Model):

    # Fields
    name = models.CharField(max_length=30, db_index=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    deadline_sjak = models.DateField()
    deadline_teknik = models.DateField()
    deadline_mad = models.DateField()
    deadline_aktivitetsteam = models.DateField()
    deadline_foto = models.DateField()
    deadline_lokaler = models.DateField()
    deadline_sos = models.DateField()


    class Meta:
        pass

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("organization_Event_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("organization_Event_update", args=(self.pk,))
    
# Create your models here.
class Team(models.Model):

    # Fields
    name = models.CharField(max_length=30, db_index=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    short_name = models.CharField(max_length=30, db_index=True)   
    events = models.ManyToManyField(Event, through='TeamEventMembership', db_index=True) 



    class Meta:
        pass

    def __str__(self):
        return str(self.name)
    

class Volunteer(models.Model):

    # Fields
    username = models.CharField(max_length=30, unique=True, db_index=True)
    first_name = models.CharField(max_length=30, db_index=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_name = models.CharField(max_length=30, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    events = models.ManyToManyField(Event, through='EventMembership',blank=True, db_index=True)
    teams = models.ManyToManyField(Team, through='TeamMembership', blank=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    

    class Meta:
        pass

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class TeamEventMembership(models.Model):

    # Relationships
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_index=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_index=True)

    # Fields
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("organization_TeamEventMembership_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("organization_TeamEventMembership_update", args=(self.pk,))


class EventMembership(models.Model):

    # Relationships
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_index=True)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, db_index=True)

    # Fields
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        pass

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse("organization_EventMembership_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("organization_EventMembership_update", args=(self.pk,))
    


