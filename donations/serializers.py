from rest_framework import serializers

from django.db import models
from categories.serializers import CategorySerializer
from .models import Donations, SavedDonations

class BasicDonationSerializer(serializers.ModelSerializer):
    """
    Basic serializer without category details to avoid recursion
    """
    collected_amount = serializers.SerializerMethodField()
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
        )
    def get_collected_amount(self, obj):
        """Calculate total from completed transactions only"""
        total = obj.transactions.filter(
            payment_status="Completed"
        ).aggregate(total=models.Sum('amount'))['total']
        return total if total else 0

class DonationSerializer(serializers.ModelSerializer):
    
    """
    serializer for Donations model
    Example Response:
           {
            "id": "dd020e75-09ea-4ceb-9eba-bf3ebb44cbd7",
            "title": "School Supplies Fund",
            "description": "Buy school supplies for children in need",
            "paybill_number": "123456",
            "account_name": "SchoolFund",
            "target_amount": "5000.00",
            "start_date": "2025-11-27T07:48:20.991862Z",
            "end_date": "2026-02-25T07:48:20.991862Z",
            "status": "Active",
            "created_at": "2025-11-27T07:48:21.016115Z",
            "updated_at": "2025-11-27T07:48:21.016141Z",
            "category": "61576472-6022-4992-b22c-35d672ae5dbb",
            "created_by": "1b45ac05-5f0a-4c0e-8cec-48592f4cbc62"
        },
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
    # category = CategorySerializer()

    class Meta:
        model = Donations
        fields = (
            "id",
            "title",
            "description",
            # 'amount',
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
    donations = serializers.SerializerMethodField()
    class Meta:
        model = SavedDonations
        fields = (
            "id",
            "donations",
            "user",
        )

    def get_donations(self, obj):
        from donations.serializers import BasicDonationSerializer
        donations = obj.donations.all() 
        return BasicDonationSerializer(donations, many=True).data

class SaveDonationSerializer(serializers.ModelSerializer):
    donation = BasicDonationSerializer()
    class Meta:
        model = SavedDonations
        fields = (
            "id",
            "donation",
            "user",
        )