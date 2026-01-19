from rest_framework import serializers

from . import models


class AktivitetsTeamItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AktivitetsTeamItem
        fields = [
            "description",
            "created",
            "last_updated",
            "name",
        ]

class AktivitetsTeamBookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AktivitetsTeamBooking
        fields = [
            "created",
            "last_updated",
            "location",
            "start_date",
            "end_date",
            "remarks",
            "status",
            "team",
            "item",
            "team_contact",
        ]
