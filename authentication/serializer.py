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
from .models import (
    UserModel,
    ClientProfileModel
)

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

class ClientProfileSerializer(ModelSerializer):
    member_since = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()
    creators_hired = serializers.SerializerMethodField()
    class Meta:
        model = ClientProfileModel
        fields = [
            'id',                
            'user', 
            'company_name', 
            'phone_no', 
            'industry', 
            'company_size', 
            'brand_description', 
            'website_url', 
            'instagram_url', 
            'linkedin_url', 
            'gst_number', 
            'pan_number', 
            'billing_address', 
            'logo', 
            'is_verified',
            'member_since',
            'total_orders',
            'creators_hired'
        ]
        read_only_fields = ['user', 'is_verified', 'id', 'member_since', 'total_orders', 'creators_hired']

    def get_member_since(self, obj):
        if obj.user and hasattr(obj.user, 'date_joined'):
            return obj.user.date_joined.strftime("%b %Y")
        return None

    def get_total_orders(self, obj):
       return 18 

    def get_creators_hired(self, obj):
        return 12


class LogoUpdateSerializer(ModelSerializer):
    class Meta:
        model = ClientProfileModel
        fields = ['logo']

    