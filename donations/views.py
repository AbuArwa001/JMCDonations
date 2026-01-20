from rest_framework import viewsets, generics, views, status

from donations.filters import DonationFilterSet
from .permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Donations, SavedDonations
from .serializers import DonationSerializer, SavedDonationSerializer
from transactions.models import Transactions
from transactions.serializers import TransactionSerializer
from reportlab.pdfgen import canvas
import io
from JMCDonations.authentication import FirebaseAuthentication
from donations import permissions
from rest_framework.decorators import action
from .models import Donations, SavedDonations
from .serializers import DonationSerializer, SavedDonationSerializer

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donations.objects.order_by('-created_at')
    serializer_class = DonationSerializer
    authentication_classes = [FirebaseAuthentication]
    filterset_class = DonationFilterSet

    def get_permissions(self):
        # Allow save/unsave for authenticated users
        if self.action in ["save", "unsave", "saved"]:
            return [IsAuthenticated()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # GET /api/v1/donations/saved/
    @action(detail=False, methods=['get'], url_path='saved')
    def saved(self, request):
        """List all donations saved by the current user"""
        saved_donations = SavedDonations.objects.filter(user=request.user)
        # We use the serializer that shows the donation details
        serializer = SavedDonationSerializer(saved_donations, many=True)
        return Response(serializer.data)

    # POST /api/v1/donations/<pk>/save/
    @action(detail=True, methods=['post'])
    def save(self, request, pk=None):
        """Save a specific donation to user's list"""
        donation = self.get_object()
        saved_donation, created = SavedDonations.objects.get_or_create(
            user=request.user, 
            donation=donation
        )
        if not created:
            return Response({"detail": "Already saved"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SavedDonationSerializer(saved_donation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # DELETE /api/v1/donations/<pk>/unsave/
    @action(detail=True, methods=['delete'])
    def unsave(self, request, pk=None):
        """Remove a specific donation from user's list"""
        donation = self.get_object()
        deleted_count, _ = SavedDonations.objects.filter(
            user=request.user, 
            donation=donation
        ).delete()
        
        if deleted_count == 0:
            return Response({"detail": "Not found in saved list"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(status=status.HTTP_204_NO_CONTENT)
class DonationHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transactions.objects.filter(user=self.request.user)


class ReceiptView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        transaction = get_object_or_404(Transactions, pk=pk, user=request.user)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, "Donation Receipt")
        p.drawString(100, 730, f"Transaction Ref: {transaction.transaction_reference}")
        p.drawString(100, 710, f"Amount: {transaction.amount}")
        p.drawString(100, 690, f"Date: {transaction.donated_at}")
        p.drawString(100, 670, f"Donation: {transaction.donation.title}")
        p.showPage()
        p.save()

        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/pdf")
