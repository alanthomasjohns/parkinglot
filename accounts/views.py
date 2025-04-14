import random
from rest_framework.views import APIView
from .models import User
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    LoginSerializer,
    # MyTokenObtainPairSerializer,
)
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Parking System API is live!"})

def generate_otp():
    return str(random.randint(100000, 999999))

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "user_id": user.id,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            print(f"kajsdnlksa{user}")
            token, created = Token.objects.get_or_create(user=user)
            current_user = user.email if user.email else user.phone_number
            return Response(
                {
                    "token": token.key,
                    "user_id": user.id,
                    "email": user.email,
                    "current_user": current_user,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPAPIView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")

        try:
            user = User.objects.get(id=user_id, otp_code=otp)
            user.is_verified = True
            user.otp_code = None  # Clear OTP
            user.save(update_fields=["is_verified", "otp_code"])
            return Response({"message": "OTP verified successfully."})
        except User.DoesNotExist:
            return Response({"error": "Invalid OTP or user."}, status=400)
