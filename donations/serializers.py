from rest_framework import serializers
from .models import Donations, SavedDonations

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donations
        fields = '__all__'

class SavedDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedDonations
        fields = '__all__'
