from rest_framework import serializers

from . import models


class SjakItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SjakItem
        fields = [
            "name",
            "description",
            "created",
            "last_updated",
            "type",
        ]

class SjakBookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SjakBooking
        fields = [
            "remarks",
            "last_updated",
            "created",
            "status",
            "quantity",
            "start",
            "end",
            "item",
            "team_contact",
            "team",
        ]


class SjakItemTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SjakItemType
        fields = [
            "name",
            "created",
            "last_updated",
        ]


