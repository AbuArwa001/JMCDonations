from rest_framework import viewsets
from .models import Ratings
from .serializers import RatingSerializer


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Ratings.objects.order_by('-id')
    serializer_class = RatingSerializer


    def perform_create(self, serializer):
        serializer.save(user=self.request.user,) 
