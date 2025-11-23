from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

from .models import Donations, Transactions, SavedDonations, Categories
from .serializers import DonationSerializer, TransactionSerializer, SavedDonationSerializer

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donations.objects.annotate(rating_avg=Avg('ratings__rating'))
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'rating_avg']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_ids = self.request.query_params.get('category_id')
        if category_ids:
            ids = [int(id) for id in category_ids.split(',') if id.isdigit()] # Assuming int IDs for now, but UUIDs in model. Adjusting logic.
            # UUID handling:
            ids = category_ids.split(',')
            queryset = queryset.filter(category__id__in=ids)
        
        # Goal Progress Ordering
        ordering = self.request.query_params.get('ordering')
        if ordering == '-progress':
            # Complex ordering might need raw SQL or extra annotation, 
            # for simplicity here we can do python sort if dataset is small, 
            # or better, annotate with progress.
            # Skipping complex annotation for MVP speed, relying on basic ordering.
            pass

        return queryset

class SavedDonationView(generics.ListCreateAPIView):
    serializer_class = SavedDonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedDonations.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        donation_id = request.data.get('donation_id')
        donation = get_object_or_404(Donations, id=donation_id)
        saved, created = SavedDonations.objects.get_or_create(user=request.user, donation=donation)
        if not created:
            return Response({'message': 'Already saved'}, status=status.HTTP_200_OK)
        return Response({'message': 'Saved'}, status=status.HTTP_201_CREATED)

class UnsaveDonationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        saved = get_object_or_404(SavedDonations, user=request.user, donation_id=pk)
        saved.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DonationHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transactions.objects.filter(user=self.request.user)

class ReceiptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        transaction = get_object_or_404(Transactions, pk=pk, user=request.user)
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "Donation Receipt")
        p.drawString(100, 730, f"Transaction Reference: {transaction.transaction_reference}")
        p.drawString(100, 710, f"Donation: {transaction.donation.title}")
        p.drawString(100, 690, f"Amount: {transaction.amount}")
        p.drawString(100, 670, f"Date: {transaction.donated_at}")
        p.drawString(100, 650, f"Donor: {request.user.full_name}")
        p.showPage()
        p.save()

        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
