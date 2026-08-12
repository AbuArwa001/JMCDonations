from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from users.views import FirebaseCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('', include('authentication.urls')),
    # API with versioning and clear prefixes
    path(
        "api/v1/",
        include(
            [
                path('check-firebase/', FirebaseCheckView.as_view(), name='check-firebase'),
                path("", include("donations.urls"), name="donations"),
                path("", include("users.urls"), name="users"),
                path("", include("analytics.urls"), name="analytics"),
                path("", include("ratings.urls"), name="ratings"),
                path("", include("categories.urls"), name="categories"),
                path(
                    "", include("transactions.urls"), name="transactions"
                ),
                path("core_config/", include("core_config.urls")),
                path("feature-toggles/", include("core_config.urls")), # Assuming core_config handles toggles
                path("", include("community.urls")),
                path("duas/", include("duas.urls")),
                path("quran/", include("quran.urls")),
                path("prayer-times/", include("prayer_times.urls")),
                path("zakat/", include("zakat.urls")),
                path("khutba/", include("khutba.urls")),
                path("events/", include("events.urls")),
                path("notifications/", include("khutba.urls")), # Register endpoint mapping
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

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
