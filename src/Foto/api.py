from rest_framework import viewsets, permissions

from . import serializers
from . import models


class FotoItemViewSet(viewsets.ModelViewSet):
    """ViewSet for the FotoItem class"""

    queryset = models.FotoItem.objects.all()
    serializer_class = serializers.FotoItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class FotoBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for the FotoBooking class"""

    queryset = models.FotoBooking.objects.all()
    serializer_class = serializers.FotoBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
