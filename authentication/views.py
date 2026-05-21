import os
import random
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permission.user_permission import UserGeneralAuthorization
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_404_NOT_FOUND
)
from core.helpers import handle_serializer_exception
from core.permission.user_permission import UserGeneralAuthorization
from core.jwt_token import generate_jwt_payload
from .serializer import (
    UserLoginSerializer, 
    UserSignupSerializer,
    ClientProfileSerializer
)
from authentication.models import (
    ClientProfileModel
)

# Create your views here.
CLIENT_JWT_KEY = os.getenv('CLIENT_JWT_KEY')
"""JWT Token"""

class UserAuthViewSet(ModelViewSet):
    @action(detail= False,methods= ['POST']) 
    def register(self, request):
        try:
            user_seriralizer = UserSignupSerializer(data = request.data)
            if not user_seriralizer.is_valid():
                return Response (
                    {
                        "status": False,
                        "message": handle_serializer_exception(user_seriralizer)
                    },
                    status= HTTP_400_BAD_REQUEST
                )
            user_instance = user_seriralizer.save() 
            token_payload = generate_jwt_payload(
                entity_instance = user_instance,
                roles = user_instance.role,
                jwt_key = CLIENT_JWT_KEY
            )
            if not token_payload["status"]:
                user_instance.delete()
                return Response (
                    {
                        "status": False,
                        "message": token_payload["message"],
                        "details": token_payload["details"]
                    },
                    status= HTTP_500_INTERNAL_SERVER_ERROR
                )
            # response_data = {
            #     "id": user_instance.id,
            #     "email": user_instance.email,
            #     "school": student_instance.school
            # }
            return Response (
                {
                    "status": True,
                    "message": "Client created successfully",
                    "access_token": token_payload["access_token"],
                    "refresh_token": token_payload["refresh_token"],
                    "data": user_seriralizer.data,
                    # "data": response_data

                },
                status= HTTP_200_OK 
                )
            
        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
    """User Login with model view set with token"""
    @action(detail= False,methods= ['POST'])
    def login(self, request):
        try:
            user_instance = UserLoginSerializer(data=request.data)
            print(user_instance)
            if not user_instance.is_valid():
                error = handle_serializer_exception(user_instance)
                return Response({"status":False,"message":error}, status=HTTP_400_BAD_REQUEST)
            
            user_data = user_instance.validated_data
            token_payload = generate_jwt_payload(
                entity_instance = user_data,
                roles = "Client",
                jwt_key = CLIENT_JWT_KEY
            )
            
            message = (
                "Client login successfully" if user_data.role == 1 else
                "Creator login successfully" if user_data.role == 2 else
                "Admin login successfully"
            )

            response_data = {
                "id": user_data.id,
                "full_name": user_data.full_name,
                "phone_no": user_data.phone_no,
                "email": user_data.email,
                "role": user_data.role,
                "image": user_data.image.url if user_data.image else None,
                "is_active": user_data.is_active
            }
            return Response (
                    {
                        "status": True,
                        "message": message,
                        "access_token": token_payload["access_token"],
                        "refresh_token": token_payload["refresh_token"],
                        "data": response_data
                        # "data": {
                        #     "id":user_data.id,
                        #     "first_name":user_data.first_name,
                        #     "last_name":user_data.last_name,
                        #     "email":user_data.email,
                        #     "role":user_data.role,
                        #     "image": user_data.image.url if user_data.image else None,
                        #     "is_active":user_data.is_active
                        # }
                    },
                    status= HTTP_200_OK
                )  

        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail= False,methods= ['GET'], permission_classes=[UserGeneralAuthorization]) 
    def client_profile_view(self, request):
        """Fetch the profile of the currently logged-in user"""
        try:
            profile = ClientProfileModel.objects.get(user=request.user_instance)
            serializer = ClientProfileSerializer(profile)
            return Response({
                "status": True, 
                "message": "Profile retrieve successfully",
                "data": serializer.data
            }, status=HTTP_200_OK)
            
        except ClientProfileModel.DoesNotExist:
            return Response({
                "status": False, 
                "message": "Profile not found. Please create one."
            }, status=HTTP_404_NOT_FOUND)
    
    @action(detail= False,methods= ['POST'], permission_classes=[UserGeneralAuthorization]) 
    def client_profile_update(self, request):
        """Create or Update the profile for the currently logged-in user"""
        try:
            profile = ClientProfileModel.objects.get(user=request.user_instance)
            serializer = ClientProfileSerializer(profile, data=request.data, partial=True)
            action_msg = "Profile updated successfully"
            
        except ClientProfileModel.DoesNotExist:
            serializer = ClientProfileSerializer(data=request.data)
            action_msg = "Profile created successfully"

        if serializer.is_valid():
            serializer.save(user=request.user_instance)
            
            return Response({
                "status": True,
                "message": action_msg,
                "data": serializer.data
            }, status=HTTP_200_OK)

        return Response({
            "status": False,
            "message": handle_serializer_exception(serializer)
        }, status=HTTP_400_BAD_REQUEST)
    
   