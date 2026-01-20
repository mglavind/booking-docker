from rest_framework import serializers

from . import models


class FotoItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.FotoItem
        fields = [
            "last_updated",
            "created",
        ]

class FotoBookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.FotoBooking
        fields = [
            "start",
            "end",
            "remarks",
            "created",
            "location",
            "last_updated",
            "status",
            "team",
            "item",
            "team_contact",
        ]
