from rest_framework import viewsets, permissions

from . import serializers
from . import models


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for the Team class"""

    queryset = models.Team.objects.all()
    serializer_class = serializers.TeamSerializer
    permission_classes = [permissions.IsAuthenticated]


class TeamMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for the TeamMembership class"""

    queryset = models.TeamMembership.objects.all()
    serializer_class = serializers.TeamMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for the Event class"""

    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for the EventMembership class"""

    queryset = models.EventMembership.objects.all()
    serializer_class = serializers.EventMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]


class VolunteerViewSet(viewsets.ModelViewSet):
    """ViewSet for the Volunteer class"""

    queryset = models.Volunteer.objects.all()
    serializer_class = serializers.VolunteerSerializer
    permission_classes = [permissions.IsAuthenticated]
