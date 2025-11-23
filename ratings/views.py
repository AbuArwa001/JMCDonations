from rest_framework import viewsets
from .models import Ratings
from .serializers import RatingSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Ratings.objects.all()
    serializer_class = RatingSerializer
