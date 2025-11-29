from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("auth/", include("drf_social_oauth2.urls", namespace="drf")),
    # API with versioning and clear prefixes
    path(
        "api/v1/",
        include(
            [
                path("", include("users.urls"), name="users"),
                path("", include("donations.urls"), name="donations"),
                path("", include("analytics.urls"), name="analytics"),
                path("ratings/", include("ratings.urls"), name="ratings"),
                path("", include("categories.urls"), name="categories"),
                path(
                    "transactions/", include("transactions.urls"), name="transactions"
                ),
            ]
        ),
    ),
    # Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Documentation with tags
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("silk/", include("silk.urls", namespace="silk")),
]

""" from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="JMCDonations API",
      default_version='v1',
      description="API documentation for JMCDonations Donation Platform",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@donations.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('api/', include('users.urls')),
    path('api/', include('donations.urls')),
    path('api/', include('analytics.urls')),
    path('api/', include('ratings.urls')),
    path('api/', include('categories.urls')),
    path('api/', include('transactions.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('silk/', include('silk.urls', namespace='silk'))
]
 """
