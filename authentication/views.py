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
from core.jwt_token import generate_jwt_payload
from .serializer import (
    UserLoginSerializer, 
    UserSignupSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    UserChangePasswordSerializer
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
    
    @action(detail=False, methods=['POST'], permission_classes=[UserGeneralAuthorization])
    def mark_guide_viewed(self, request):
        try:
            user = request.user_instance
            
            # Check if user is a student
            if user.role != 1:
                return Response({"status": False, "message": "Only students can perform this action."}, status=HTTP_400_BAD_REQUEST)
            
            student_profile = getattr(user, 'student_profile', None)
            if not student_profile:
                return Response({"status": False, "message": "Student profile not found."}, status=HTTP_404_NOT_FOUND)
                
            # Flag ko true mark kar ke save kar dein
            student_profile.insight_guide_viewed = True
            student_profile.save()
            
            return Response({
                "status": True, 
                "message": "Insight guide marked as viewed successfully."
            }, status=HTTP_200_OK)

        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    # @action(detail=False, methods=["POST"])
    # def send_reset_email(self, request):
    #     try:
    #         serializer = ForgotPasswordSerializer(data=request.data)
    #         if not serializer.is_valid():
    #             error = handle_serializer_exception(serializer)

    #             return Response(
    #                     {"status": False, "message": error},
    #                     status=HTTP_400_BAD_REQUEST,
    #             )  
            
    #         # Generate OTP and update user
    #         otp = random.randint(10000, 99999)  # Ensures exactly 5 digits
            
    #         user = serializer.user
    #         user.otp = otp
    #         user.save()

    #         subject = "Forget Password"
    #         message = f"Hi {user.first_name},\n\nYour OTP to reset your password is: {otp}"
    #         recipient = [user.email]
            
    #         send_mail(
    #             subject,
    #             message,
    #             settings.DEFAULT_FROM_EMAIL,
    #             recipient,
    #             fail_silently=False,
    #         )
    #         return Response({"statue":True,"message": "Password reset email sent."}, status=HTTP_200_OK)
        
    #     except Exception as error:
    #         return Response(
    #             {"status": False, "error": str(error)},
    #             status=HTTP_500_INTERNAL_SERVER_ERROR,
    #         )

    @action(detail=False, methods=["POST"])
    def send_reset_email(self, request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                error = handle_serializer_exception(serializer)
                return Response(
                    {"status": False, "message": error},
                    status=HTTP_400_BAD_REQUEST,
                )  
            
            # Generate OTP and update user
            otp = random.randint(10000, 99999)  # Ensures exactly 5 digits
            
            user = serializer.user
            user.otp = otp
            user.save()

            subject = "Your Password Reset Code"
            
            html_message = render_to_string('emails/otp_email.html', {
                'first_name': user.first_name,
                'otp': otp
            })
            
            plain_message = strip_tags(html_message)
            
            recipient = [user.email]
            
            send_mail(
                subject=subject,
                message=plain_message,          # Fallback plain text
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient,
                html_message=html_message,      # Asli HTML message
                fail_silently=False,
            )
            
            # "statue" typo fixed to "status"
            return Response({"status": True, "message": "Password reset email sent."}, status=HTTP_200_OK)
        
        except Exception as error:
            return Response(
                {"status": False, "error": str(error)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=["POST"])
    def verify_otp(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            if not serializer.is_valid():
                error = handle_serializer_exception(serializer)
                return Response(
                    {"status": False, "message": error},
                    status=HTTP_400_BAD_REQUEST
                )
            return Response(
                    {"status": True, "message": "OTP verified successfully"},
                    status=HTTP_200_OK,
                )
        except Exception as error:
            return Response(
                {"status": False, "error": str(error)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=["POST"])
    def reset_password(self, request):
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                error = handle_serializer_exception(serializer)
                return Response(
                    {"status": False, "message": error},
                    status=HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                {"status": True, "message": "Password updated successfully."},
                status=HTTP_200_OK,
            )
        except Exception as error:
            return Response(
                {"status": False, "error": str(error)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
    @action(detail=False, methods=['POST'], permission_classes=[UserGeneralAuthorization])
    def change_password(self, request):
        serializer = UserChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Password changed successfully."}, status=HTTP_200_OK)
        return Response({"status": False, "errors": handle_serializer_exception(serializer)}, status=HTTP_400_BAD_REQUEST)