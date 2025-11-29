from rest_framework import serializers
from .models import Categories


class BasicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ("id", "category_name")

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    donations = serializers.SerializerMethodField()

    class Meta:
        model = Categories
        fields = ("id", "category_name", "donations")

    def get_donations(self, obj):
        from donations.serializers import BasicDonationSerializer
        donations = obj.donations.all() 
        return BasicDonationSerializer(donations, many=True).data