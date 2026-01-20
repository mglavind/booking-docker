from rest_framework import viewsets, permissions

from . import serializers
from . import models


class TeknikBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for the TeknikBooking class"""

    queryset = models.TeknikBooking.objects.all()
    serializer_class = serializers.TeknikBookingSerializer
    permission_classes = [permissions.IsAuthenticated]


class TeknikItemViewSet(viewsets.ModelViewSet):
    """ViewSet for the TeknikItem class"""

    queryset = models.TeknikItem.objects.all()
    serializer_class = serializers.TeknikItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class TeknikTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for the TeknikType class"""

    queryset = models.TeknikType.objects.all()
    serializer_class = serializers.TeknikTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
