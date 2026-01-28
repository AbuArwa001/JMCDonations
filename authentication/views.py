from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from .backends import FirebaseDRFAuthentication

class AdminFirebaseBridge(APIView):
    """
    Exchange a Firebase Token for a Django Session Cookie 
    so you can access /admin/
    """
    def post(self, request):
        # 1. Use your existing logic to verify the user
        auth_instance = FirebaseDRFAuthentication()
        user_tuple = auth_instance.authenticate(request)
        
        if user_tuple:
            user, _ = user_tuple
            # 2. Start a standard Django Session
            # This sets the 'sessionid' cookie in your browser
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return Response({"detail": "Session started. You can now go to /admin/"})
        
        return Response({"error": "Invalid Token"}, status=400)