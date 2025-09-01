import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .permissions import (
    IsAdmin,
    IsAuthenticated
)

from .serializers import (
    ChangePasswordAdminSerializer,
    RegistrationSerializer,
    UserSerializer,
    UserSearchSerializer,
    UserRoleSerializer
)

class UserRoleListAPIView(APIView):
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request._user
        if user and user.is_authenticated:
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            reader = {
                "role" : "reader"
            }
        return Response(reader, status=status.HTTP_200_OK)
    
class RegistrationAPIView(APIView):
    serializer_class = RegistrationSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = User.generate_activation_token(user.id)
            message = f"Click the following link to activate your account: {settings.WEBSITE_BASE_URL}activation/{token}/"
            send_mail(
                subject="Activate your account",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordAPIView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            email = request.data.get('email');
            if email:
                user = User.objects.get(email=email)
                if user:
                    token = User.generate_reset_token(user.id)
                    message = f"Click the following link to reset your password: {settings.WEBSITE_BASE_URL}password/reset/{token}/"
                    send_mail(
                        subject="Reset your password",
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    return Response(status=status.HTTP_200_OK)
        except:
            # Always return okay to avoid leading emails
            return Response(status=status.HTTP_200_OK)

class ApplyResetPasswordAPIView(APIView):
    permission_classes = []

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_201_CREATED)
        except jwt.exceptions.ExpiredSignatureError:
            return Response(
                {"detail": "The activation link has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (jwt.exceptions.DecodeError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class ActivationAPIView(APIView):
    permission_classes = []

    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({"detail": "Your account has been activated."})
        except jwt.exceptions.ExpiredSignatureError:
            return Response(
                {"detail": "The activation link has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (jwt.exceptions.DecodeError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LastUsersAPIView(APIView):
    queryset = User.objects.order_by("-date_joined")[:10]

    def get(self, request):
        users = User.objects.order_by("-date_joined")[:10]
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UsersListAPIView(APIView):
    queryset = User.objects.order_by("-date_joined")

    def get(self, request):
        search_query = request.query_params.get("q", None)
        if search_query:
            queryset = self.queryset.filter(
                Q(alias__icontains=search_query) | Q(email__icontains=search_query)
            ).distinct()
        else:
            queryset = self.queryset

        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = UserSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordAdminSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    lookup_field = "email"

    def get_object(self):
        return self.queryset.get(email=self.kwargs.get("email"))

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            password = serializer.validated_data["password"]
            user.set_password(password)
            user.save()
            return Response({"status": "password set"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DisableUserAPIView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, email):
        user = get_object_or_404(User, email=email)

        user.is_active = False
        user.save()

        return Response(
            {"detail": f"User {email} has been disabled"}, status=status.HTTP_200_OK
        )

class AuthorRetrieveView(generics.RetrieveAPIView):
    lookup_field = "id"
    queryset = User.objects.all()
    serializer_class = UserSearchSerializer