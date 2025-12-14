from django.urls import include, path
from .views import (
    DashboardSummaryView,
    CategoryBreakdownView,
    DriveProgressView,
    PendingCashView,
    ExportView,
    DonationTrendsView,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"/", DashboardSummaryView, basename="dashboard")
# router.register(r'analytics', DashboardSummaryView, basename='dashboard')


urlpatterns = [
    path(
        "analytics/",
        include(
            [
                path(
                    "summary/", DashboardSummaryView.as_view(), name="dashboard-summary"
                ),
                path(
                    "categories/",
                    CategoryBreakdownView.as_view(),
                    name="category-breakdown",
                ),
                path(
                    "donations/<uuid:pk>/progress/",
                    DriveProgressView.as_view(),
                    name="drive-progress",
                ),
                path("cash/pending/", PendingCashView.as_view(), name="pending-cash"),
                path("export/", ExportView.as_view(), name="data-export"),
                path("trends/", DonationTrendsView.as_view(), name="donation-trends"),
            ]
        ),
    ),
]
# urlpatterns += router.urls
