from rest_framework import serializers

from django.db import models
from categories.serializers import CategorySerializer
from .models import Donations, SavedDonations, DonationImage

class BasicDonationSerializer(serializers.ModelSerializer):
    """
    Basic serializer without category details to avoid recursion
    """
    collected_amount = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    class Meta:
        model = Donations
        fields = (
            "id",
            "title",
            "description",
            "target_amount",
            "start_date",
            "end_date",
            "status",
            "paybill_number",
            "account_name",
            "created_at",
            "collected_amount",
            "is_saved",
        )
    def get_is_saved(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return SavedDonations.objects.filter(user=user, donation=obj).exists()
        return False
    def get_collected_amount(self, obj):
        """Calculate total from completed transactions only"""
        total = obj.transactions.filter(
            payment_status="Completed"
        ).aggregate(total=models.Sum('amount'))['total']
        return total if total else 0

class DonationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationImage
        fields = ("id", "image", "donation", "created_at")

class DonationSerializer(serializers.ModelSerializer):
    
    """
    serializer for Donations model
    """
    def get_avg_rating(self, obj):
        return obj.average_rating()
    def get_donor_count(self, obj):
        return obj.donor_count()
    def get_collected_amount(self, obj):
        """Calculate total from completed transactions only"""
        total = obj.transactions.filter(
            payment_status="Completed"
        ).aggregate(total=models.Sum('amount'))['total']
        return total if total else 0
    
    collected_amount = serializers.SerializerMethodField()
    donor_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    images = DonationImageSerializer(many=True, read_only=True)

    def get_is_saved(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return SavedDonations.objects.filter(user=user, donation=obj).exists()
        return False

    class Meta:
        model = Donations
        fields = (
            "id",
            "title",
            "description",
            "images",
            "created_at",
            "account_name",
            "target_amount",
            "start_date",
            "end_date",
            "status",
            "avg_rating",
            "paybill_number",
            "category",
            "donor_count",
            "collected_amount",
            "is_saved",
        )
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'account_name': {'required': False},
            'target_amount': {'required': False},
            'start_date': {'required': False},
            'end_date': {'required': False},
            'status': {'required': False},
            'paybill_number': {'required': False},
            'category': {'required': False},
        }
        read_only_fields = ('id', 'created_at', 'avg_rating')
    

    # def perform_create(self, serializer):
    #     serializer.save(created_by=self.context["request"].user)

class SavedDonationSerializer(serializers.ModelSerializer):
    # This automatically uses the serializer for the linked donation object
    donation = BasicDonationSerializer(read_only=True)

    class Meta:
        model = SavedDonations
        fields = ("id", "donation", "user", "saved_at")
class SaveDonationSerializer(serializers.ModelSerializer):
    donation = BasicDonationSerializer()
    class Meta:
        model = SavedDonations
        fields = (
            "id",
            "donation",
            "user",
        )