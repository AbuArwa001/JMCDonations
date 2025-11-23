from django.urls import path
from .views import DashboardSummaryView, CategoryBreakdownView, DriveProgressView, PendingCashView, ExportView

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('categories/', CategoryBreakdownView.as_view(), name='category-breakdown'),
    path('donations/<uuid:pk>/progress/', DriveProgressView.as_view(), name='drive-progress'),
    path('cash/pending/', PendingCashView.as_view(), name='pending-cash'),
    path('export/', ExportView.as_view(), name='data-export'),
]
