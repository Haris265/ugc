import jwt
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from core import usable as uc
from django.conf import settings
from passlib.hash import django_pbkdf2_sha256 as handler
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    ValidationError,
    ValidationError,
    EmailField
)
from .models import UserModel

class UserSignupSerializer(ModelSerializer):
    """Serializer for user signup with validations"""
    password = CharField(write_only=True, min_length=8, required=True)
    # confirm_password = CharField(write_only=True, required=True)
    
    class Meta:
        model = UserModel  
        fields = ["id", "full_name", "phone_no", "email", "password", "role", "is_active"]
        
    def validate(self, data): 
        """Custom validation for password matching and email formatting"""
        data["email"] = data["email"].lower().strip()  
        # if data["password"] != data["confirm_password"]:
        #     raise ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create a new user with hashed password"""
        # validated_data.pop("confirm_password")  
        return UserModel.objects.create(**validated_data)
    
    


class UserLoginSerializer(Serializer):
    """User Login Serializer"""
    
    email = EmailField(required=True)
    password = CharField(write_only=True, required=True)

    def validate(self, data):
        """Validate email and password"""
        email = data["email"].lower().strip() 
        password = data["password"]

        user = UserModel.objects.filter(email=email).first()
        if not user:
            raise ValidationError({"email": "User with this email does not exist"})

        if not check_password(password, user.password):
            raise ValidationError({"password": "Incorrect password"})
        
        if not user.is_active:
            raise ValidationError({"email": "This account is disabled"})
        
        return user
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        user = UserModel.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("No user is associated with this email.")
        
        self.user = user  # Store user instance
        return value
    
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")

        user = UserModel.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("No user is associated with this email.")
        
        if user.otp == otp:
            # Reset OTP count and mark as verified
            user.otp_count = 0
            user.otp_status = False  # Once verified, expire the OTP
            user.otp = None
            user.save()
            return data
        
        user.otp_count += 1
        if user.otp_count >= 3:
            user.otp_status = False  # Expire OTP after 3 failed attempts
            user.otp = None
            user.save()
            
            if not user.otp_status:
                raise serializers.ValidationError("OTP has expired")
            raise serializers.ValidationError("Invalid OTP. Please try again.")
        return data

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # 1. Check if both passwords match
        if password != confirm_password:
            raise serializers.ValidationError({
                "password": "Password and Confirm Password do not match."
            })

        # 2. Check if user exists
        user = UserModel.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("No user is associated with this email.")

        # 3. Check OTP Status
        # if not user.otp_status:
        #     raise serializers.ValidationError("OTP has expired or is invalid.")

        # # 4. Verify OTP
        # if user.otp != otp:
        #     user.otp_count += 1
        #     if user.otp_count >= 3:
        #         user.otp_status = False  # Expire OTP after 3 failed attempts
        #         user.otp = None          # Remove OTP
        #         user.otp_count = 0
        #     user.save()
        #     raise serializers.ValidationError("Invalid OTP. Please try again.")

        self.user = user
        return data

    def save(self):
        user = self.user
        password = self.validated_data["password"]

        user.password = handler.hash(password) 
        
        user.otp = None  
        user.otp_status = False
        user.otp_count = 0  
        user.save()


class UserChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        user = self.context['request'].user_instance

        # Check if current password is correct
        if not check_password(data['current_password'], user.password):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})

        # Check if new password and confirm password match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match."})

        # Optional: Check if new password is different from current
        if data['current_password'] == data['new_password']:
            raise serializers.ValidationError({"new_password": "New password must be different from current password."})

        return data

    def save(self, **kwargs):
        user = self.context['request'].user_instance
        user.password = make_password(self.validated_data['new_password'])
        user.save()
        return user
    