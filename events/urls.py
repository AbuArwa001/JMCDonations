from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventCategoryViewSet, EventViewSet, EventNotifyView, EventImageViewSet

router = DefaultRouter()
router.register(r'categories', EventCategoryViewSet, basename='event-category')
router.register(r'images', EventImageViewSet, basename='event-image')
router.register(r'', EventViewSet, basename='event')

urlpatterns = [
    path('<int:pk>/notify/', EventNotifyView.as_view(), name='event-notify'),
    path('', include(router.urls)),
]
