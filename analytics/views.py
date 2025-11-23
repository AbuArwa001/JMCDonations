from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db import models
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from donations.models import Donations
from transactions.models import Transactions
from categories.models import Categories
import openpyxl
from datetime import datetime

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin

class DashboardSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_collected = Transactions.objects.filter(payment_status='Completed').aggregate(Sum('amount'))['amount__sum'] or 0
        active_drives = Donations.objects.filter(status='Active').count()
        return Response({
            'total_collected': total_collected,
            'active_drives': active_drives
        })

class CategoryBreakdownView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = Categories.objects.annotate(
            total_amount=Sum('donations__transactions__amount', filter=models.Q(donations__transactions__payment_status='Completed'))
        ).values('category_name', 'total_amount')
        return Response(data)

class DriveProgressView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        donation = Donations.objects.get(pk=pk)
        total_collected = donation.transactions.filter(payment_status='Completed').aggregate(Sum('amount'))['amount__sum'] or 0
        unique_donors = donation.transactions.filter(payment_status='Completed').values('user').distinct().count()
        return Response({
            'donation': donation.title,
            'total_collected': total_collected,
            'unique_donors': unique_donors,
            'target': donation.target_amount
        })

class PendingCashView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        transactions = Transactions.objects.filter(payment_method='Cash', payment_status='Pending')
        data = [{'id': t.id, 'amount': t.amount, 'donation': t.donation.title} for t in transactions]
        return Response(data)

class ExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        drive_id = request.query_params.get('drive_id')
        queryset = Transactions.objects.all()
        
        if drive_id:
            queryset = queryset.filter(donation__id=drive_id)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=transactions_{datetime.now().strftime("%Y%m%d")}.xlsx'

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transactions"

        headers = ['ID', 'Donation', 'User', 'Amount', 'Status', 'Date', 'Reference']
        ws.append(headers)

        for t in queryset:
            ws.append([
                str(t.id),
                t.donation.title,
                t.user.email if t.user else 'Anonymous',
                t.amount,
                t.payment_status,
                t.donated_at.strftime("%Y-%m-%d %H:%M:%S"),
                t.transaction_reference
            ])

        wb.save(response)
        return response
