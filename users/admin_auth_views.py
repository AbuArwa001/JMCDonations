from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.views import View
from django.http import JsonResponse
from firebase_admin import auth
import json

class FirebaseAdminLoginView(View):
    """
    View to handle Firebase login for Django Admin.
    Can be called via POST with an idToken.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            id_token = data.get('idToken')
            
            if not id_token:
                return JsonResponse({'error': 'No ID token provided'}, status=400)
            
            # Authenticate using the custom FirebaseBackend
            user = authenticate(request, id_token=id_token)
            
            if user:
                login(request, user, backend='authentication.backends.FirebaseBackend')
                return JsonResponse({'status': 'success', 'redirect': '/admin/'})
            else:
                return JsonResponse({'error': 'Unauthorized or invalid token'}, status=401)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request):
        # Provide a simple debug page or instructions
        return JsonResponse({
            'message': 'Post your Firebase idToken to this endpoint to login to Django Admin.',
            'example': 'curl -X POST -H "Content-Type: application/json" -d \'{"idToken": "YOUR_TOKEN"}\' http://localhost:8000/api/v1/users/admin-firebase-login/'
        })
