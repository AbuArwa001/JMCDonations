from rest_framework import viewsets, generics, views, status
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

from donations import permissions


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donations.objects.all()
    serializer_class = DonationSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SavedDonationView(generics.ListCreateAPIView):
    serializer_class = SavedDonationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedDonations.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Handle creation from URL pk if provided, else expect donation_id in body
        donation_id = self.kwargs.get("pk")
        if donation_id:
            donation = get_object_or_404(Donations, pk=donation_id)
            serializer.save(user=self.request.user, donation=donation)
        else:
            serializer.save(user=self.request.user)


class UnsaveDonationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        saved_donation = get_object_or_404(
            SavedDonations, user=request.user, donation_id=pk
        )
        saved_donation.delete()
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
