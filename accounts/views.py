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


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered. OTP sent."},
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


# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer


class VerifyOTPAPIView(APIView):
    def post(self, request):
        email_or_phone = request.data.get('email') or request.data.get('phone_number')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email_or_phone) if '@' in email_or_phone else User.objects.get(phone_number=email_or_phone)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.otp_code != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        # Optional: Check expiry (e.g., 5 min)
        time_diff = timezone.now() - user.otp_created_at
        if time_diff.total_seconds() > 300:
            return Response({"error": "OTP expired"}, status=400)

        user.is_active = True
        user.is_verified = True
        user.otp_code = None
        user.otp_created_at = None
        user.save()

        return Response({"message": "User verified successfully"})
