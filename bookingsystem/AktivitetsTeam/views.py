from django.shortcuts import render
from rest_framework import viewsets
from .models import AktivitetsTeamBooking
from .serializers import AktivitetsTeamBookingSerializer

class AktivitetsTeamBookingViewSet(viewsets.ModelViewSet):
    queryset = AktivitetsTeamBooking.objects.all()
    serializer_class = AktivitetsTeamBookingSerializer