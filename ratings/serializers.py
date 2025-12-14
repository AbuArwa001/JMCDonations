from rest_framework import serializers
from .models import Ratings


class RatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Ratings
        fields = (
            "id",
            "user",
            "user_name",
            "donation",
            "comment",
            "rating",
            "created_at",
            "updated_at",
        )
