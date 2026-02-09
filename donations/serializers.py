from rest_framework import serializers
from django.db import models
from categories.serializers import CategorySerializer
from .models import Donations, SavedDonations
import boto3
from django.conf import settings
from django.utils import timezone


def upload_donation_images_to_s3(donation_instance, image_files):
    """
    Uploads a list of files to S3 and returns the list of public URLs.
    Path: [bucket_name]/[slug]/[filename]
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    urls = []
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    for i, file_obj in enumerate(image_files[:5]):  # Limit to 5 images
        # Generate path: slug/filename.jpg
        file_path = f"{donation_instance.slug}/{file_obj.name}"
        
        # Upload to S3
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            file_path,
            ExtraArgs={
                'ContentType': file_obj.content_type
            }
        )
        
        # Construct the URL
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
        urls.append(url)
    
    return urls
class BasicDonationSerializer(serializers.ModelSerializer):
    """
    Basic serializer without category details to avoid recursion
    """
    collected_amount = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    class Meta:
        model = Donations
        fields = (
            "id",
            "title",
            "is_featured",
            "description",
            "target_amount",
            "start_date",
            "end_date",
            "status",
            "paybill_number",
            "account_name",
            "created_at",
            "collected_amount",
            "image_urls",
            "uploaded_images",
        )
        read_only_fields = ('id', 'created_at', 'avg_rating', 'image_urls')
    def get_collected_amount(self, obj):
        """Calculate total from completed transactions only"""
        total = obj.transactions.filter(
            payment_status="Completed"
        ).aggregate(total=models.Sum('amount'))['total']
        return total if total else 0

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
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        required=False
    )
    remaining_days = serializers.ReadOnlyField()
    class Meta:
        model = Donations
        fields = (
            "id",
            "title",
            "is_featured",
            "description",
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
            "image_urls",
            "remaining_days",
            "uploaded_images",
        )
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'account_name': {'required': False},
            'start_date': {'required': False},
            'end_date': {'required': False},
            'status': {'required': False},
            'paybill_number': {'required': False},
            'category': {'required': False},
        }
        read_only_fields = ('id', 'created_at', 'avg_rating')
    def create(self, validated_data):
        print(validated_data)
        images = validated_data.pop('uploaded_images', [])
        donation = Donations.objects.create(**validated_data)
            
        if images:
            urls = upload_donation_images_to_s3(donation, images)
            donation.image_urls = urls
            donation.save()
        return donation
    def update(self, instance, validated_data):
        print(validated_data)
        images = validated_data.pop('uploaded_images', [])
        instance = super().update(instance, validated_data)
        if images:
            urls = upload_donation_images_to_s3(instance, images)
            
            # Ensure image_urls is a list
            if instance.image_urls is None:
                instance.image_urls = []
            elif not isinstance(instance.image_urls, list):
                # Handle case where it might be stored incorrectly or as a string
                instance.image_urls = list(instance.image_urls)
                
            instance.image_urls.extend(urls)
            instance.save()
        return instance

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