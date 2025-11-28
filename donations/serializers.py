from rest_framework import serializers
from .models import Donations, SavedDonations


 
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
    class Meta:
        model = Donations
        fields = (
            'id',
            'title',
            'description',
            # 'amount',
            'created_at',
            'account_name',
            'target_amount',
            'start_date',
            'end_date',
            'status',
            'paybill_number',
            'category',
        )

class SavedDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedDonations
        fields = '__all__'
