from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import NisabRate
from .serializers import NisabRateSerializer

class NisabRateAPIView(views.APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request, *args, **kwargs):
        rate = NisabRate.load()
        serializer = NisabRateSerializer(rate)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        rate = NisabRate.load()
        serializer = NisabRateSerializer(rate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)
