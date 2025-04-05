from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'username', 'password']

    def validate(self, data):
        if not data.get('email') and not data.get('phone_number'):
            raise serializers.ValidationError("Either email or phone number is required.")
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        phone = data.get('phone_number')
        password = data.get('password')

        if not email and not phone:
            raise serializers.ValidationError("Enter either email or phone number.")

        user = None
        if email:
            user = authenticate(username=email, password=password)
        elif phone:
            try:
                user_obj = User.objects.get(phone_number=phone)
                user = authenticate(username=user_obj.email, password=password)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid phone number or password.")

        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number')
        read_only_fields = ['email']


# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['full_name'] = user.full_name
#         token['email'] = user.email
#         return token

#     def validate(self, attrs):
#         data = super().validate(attrs)
#         data['user_id'] = self.user.id
#         data['full_name'] = self.user.full_name
#         data['email'] = self.user.email
#         return data
