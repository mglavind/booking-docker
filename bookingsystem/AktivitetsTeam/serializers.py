from rest_framework import serializers
from .models import AktivitetsTeamBooking

class AktivitetsTeamBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AktivitetsTeamBooking
        fields = '__all__'