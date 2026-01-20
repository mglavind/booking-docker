from rest_framework import serializers

from . import models


class TeknikBookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TeknikBooking
        fields = [
            "quantity",
            "created",
            "end",
            "start",
            "last_updated",
            "status",
            "team",
            "item",
            "team_contact",
        ]

class TeknikItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TeknikItem
        fields = [
            "name",
            "last_updated",
            "created",
            "description",
        ]

class TeknikTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.TeknikType
        fields = [
            "name",
            "last_updated",
            "created",
        ]
