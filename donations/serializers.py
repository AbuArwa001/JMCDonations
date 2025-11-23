from rest_framework import serializers
from .models import Donations, Categories, Transactions, SavedDonations, Ratings
from users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Categories.objects.all(), source='category', write_only=True
    )
    rating_avg = serializers.FloatField(read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Donations
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def get_progress(self, obj):
        total_collected = sum(t.amount for t in obj.transactions.filter(payment_status='Completed'))
        if obj.target_amount > 0:
            return (total_collected / obj.target_amount) * 100
        return 0

class TransactionSerializer(serializers.ModelSerializer):
    donation_title = serializers.CharField(source='donation.title', read_only=True)

    class Meta:
        model = Transactions
        fields = '__all__'
        read_only_fields = ('transaction_reference', 'donated_at', 'completed_at', 'recorded_by_admin_id')

class SavedDonationSerializer(serializers.ModelSerializer):
    donation = DonationSerializer(read_only=True)

    class Meta:
        model = SavedDonations
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ratings
        fields = '__all__'
