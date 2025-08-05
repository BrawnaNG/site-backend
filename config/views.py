from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from accounts.models import User
import requests
import os

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        if not data["username"] and data["email"]:
            find_user = User.objects.get(email__iexact = data["email"])
            if find_user:
                data["username"] = find_user.username
                del data["email"]

        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_recaptcha(request):
    # Get the token from the request
    token = request.data.get('token')
    
    if not token:
        return Response({
            'success': False,
            'error': 'reCAPTCHA token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the secret key from environment variables
    secret_key = os.getenv('RECAPTCHA_SECRET_KEY')
    
    if not secret_key:
        return Response({
            'success': False,
            'error': 'reCAPTCHA secret key not configured'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Verify the token with Google's reCAPTCHA API
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    
    data = {
        'secret': secret_key,
        'response': token
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(verify_url, data=data, headers=headers)
        result = response.json()
        
        if result.get('success'):
            return Response({
                'success': True,
                'score': result.get('score'),
                'action': result.get('action'),
                'hostname': result.get('hostname')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'reCAPTCHA verification failed',
                'error_codes': result.get('error-codes', [])
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.RequestException as e:
        return Response({
            'success': False,
            'error': 'Failed to verify reCAPTCHA due to network error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
