from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db import models
from django.db.models import Sum
from django.http import HttpResponse
from donations.models import Donations
from transactions.models import Transactions
from categories.models import Categories
import openpyxl
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from authentication.backends import FirebaseDRFAuthentication
from donations.permissions import IsAdminUser

class DashboardSummaryView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [FirebaseDRFAuthentication]

    def get(self, request):
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Total Collected (All Time)
        total_collected = (
            Transactions.objects.filter(payment_status="Completed").aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )

        # Total Collected (Week)
        total_collected_week = (
            Transactions.objects.filter(
                payment_status="Completed", donated_at__gte=week_ago
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        # Total Collected (Month)
        total_collected_month = (
            Transactions.objects.filter(
                payment_status="Completed", donated_at__gte=month_ago
            ).aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        # Active Drives
        active_drives = Donations.objects.filter(status="Active").count()

        # Donation Trends (Last 7 Days)
        trends_data = (
            Transactions.objects.filter(
                payment_status="Completed", donated_at__gte=week_ago
            )
            .annotate(date=TruncDate("donated_at"))
            .values("date")
            .annotate(amount=Sum("amount"))
            .order_by("date")
        )

        # Format trends for frontend
        trends = []
        for i in range(7):
            date = (now - timedelta(days=6 - i)).date()
            day_data = next((item for item in trends_data if item["date"] == date), None)
            trends.append({
                "name": date.strftime("%a"), # Mon, Tue, etc.
                "amount": day_data["amount"] if day_data else 0
            })

        return Response(
            {
                "total_collected": total_collected,
                "total_collected_week": total_collected_week,
                "total_collected_month": total_collected_month,
                "active_drives": active_drives,
                "donation_trends": trends,
            }
        )


class CategoryBreakdownView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [FirebaseDRFAuthentication]

    def get(self, request):
        data = Categories.objects.annotate(
            total_amount=Sum(
                "donations__transactions__amount",
                filter=models.Q(donations__transactions__payment_status="Completed"),
            )
        ).values("category_name", "total_amount", "color")
        return Response(data)


class DriveProgressView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [FirebaseDRFAuthentication]

    def get(self, request, pk):
        donation = Donations.objects.get(pk=pk)
        total_collected = (
            donation.transactions.filter(payment_status="Completed").aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )
        unique_donors = (
            donation.transactions.filter(payment_status="Completed")
            .values("user")
            .distinct()
            .count()
        )
        return Response(
            {
                "donation": donation.title,
                "total_collected": total_collected,
                "unique_donors": unique_donors,
                "target": donation.target_amount,
            }
        )


class PendingCashView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [FirebaseDRFAuthentication]

    def get(self, request):
        transactions = Transactions.objects.filter(
            payment_method="Cash", payment_status="Pending"
        )
        data = [
            {"id": t.id, "amount": t.amount, "donation": t.donation.title}
            for t in transactions
        ]
        return Response(data)


class ExportView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [FirebaseDRFAuthentication]

    def get(self, request):
        drive_id = request.query_params.get("drive_id")
        queryset = Transactions.objects.all()

        if drive_id:
            queryset = queryset.filter(donation__id=drive_id)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transactions"

        headers = ["ID", "Donation", "User", "Amount", "Status", "Date", "Reference"]
        ws.append(headers)

        for t in queryset:
            ws.append(
                [
                    str(t.id),
                    t.donation.title,
                    t.user.email if t.user else "Anonymous",
                    t.amount,
                    t.payment_status,
                    t.donated_at.strftime("%Y-%m-%d %H:%M:%S"),
                    t.transaction_reference,
                ]
            )

        wb.save(response)
        return response
class DonationTrendsView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [FirebaseDRFAuthentication]

    def get(self, request):
        period = request.query_params.get("period", "week")
        now = timezone.now()
        
        if period == "week":
            start_date = now - timedelta(days=7)
            trunc_func = TruncDate("donated_at")
            date_format = "%a" # Mon, Tue
            days_range = 7
        elif period == "month":
            start_date = now - timedelta(days=30)
            trunc_func = TruncDate("donated_at")
            date_format = "%d %b" # 01 Jan
            days_range = 30
        elif period == "year":
            start_date = now - timedelta(days=365)
            trunc_func = TruncDate("donated_at") # Grouping by month would be better for year, but keeping simple for now
            date_format = "%b" # Jan
            days_range = 365
        else:
            return Response({"error": "Invalid period"}, status=400)

        # Base query
        queryset = Transactions.objects.filter(
            payment_status="Completed", 
            donated_at__gte=start_date
        )

        # Group by date
        trends_data = (
            queryset.annotate(date=trunc_func)
            .values("date")
            .annotate(amount=Sum("amount"))
            .order_by("date")
        )

        # Format for frontend
        trends = []
        
        if period == "year":
             # For year, let's group by month manually or use TruncMonth if imported
             # For simplicity/consistency with current imports, let's just return the data points we have
             # A better approach for year is usually 12 months.
             # Let's stick to the requested logic:
             pass 

        # Re-using the logic from DashboardSummaryView but making it dynamic
        # For 'week' and 'month', we want to fill in missing days.
        
        if period in ["week", "month"]:
            for i in range(days_range):
                date = (now - timedelta(days=(days_range - 1) - i)).date()
                day_data = next((item for item in trends_data if item["date"] == date), None)
                trends.append({
                    "name": date.strftime(date_format),
                    "amount": day_data["amount"] if day_data else 0
                })
        else:
             # For year, just return the data points found, or group by month if we had TruncMonth
             # Let's return the raw daily data for now, frontend can handle or we can improve later
             for item in trends_data:
                 trends.append({
                     "name": item["date"].strftime("%d %b"),
                     "amount": item["amount"]
                 })

        return Response(trends)
