from rest_framework import serializers
from .models import Ratings


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields = (
            "id",
            "user",
            "donation",
            "comment",
            "rating",
            "created_at",
            "updated_at",
        )
