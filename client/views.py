from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.permission.user_permission import UserGeneralAuthorization
from core.helpers import handle_serializer_exception
from client.serializer import(
    CampaignCreateSerializer,
    CampaignViewSerializer
)
from client.models import (
    CampaignModel
)
from authentication.models import (
    ClientProfileModel
)

class CampaignViewSet(ModelViewSet):
    @action(detail=False, methods=['POST'], permission_classes=[UserGeneralAuthorization]) 
    def campaign_create(self, request):
        try:
            try:
                client_profile = ClientProfileModel.objects.get(user=request.user_instance)
            except ClientProfileModel.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Client profile not found for this user. Please create a profile first."
                }, status=status.HTTP_404_NOT_FOUND)

            campaign_serializer = CampaignCreateSerializer(data=request.data)
            
            if not campaign_serializer.is_valid():
                return Response({
                    "status": False,
                    "message": handle_serializer_exception(campaign_serializer) 
                }, status=status.HTTP_400_BAD_REQUEST)
                
            campaign_serializer.save(client=client_profile)
            
            return Response({
                "status": True,
                "message": "Campaign successfully created",
                "data": campaign_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as swr:
            return Response({
                "status": False, 
                "message": str(swr)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail= False,methods= ['GET'],permission_classes=[UserGeneralAuthorization]) 
    def campaign_view(self, request):
        try:
            campaigns = CampaignModel.objects.filter(client__user=request.user_instance)
            serializer = CampaignViewSerializer(campaigns, many=True)
            return Response ({
                "status": True,
                "message": "Campaign retrieve successfully",
                "data": serializer.data
            })
        
        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, url_path="campaign_delete/(?P<pk>[0-9a-f-]+)", methods=['DELETE'], permission_classes=[UserGeneralAuthorization])
    def campaign_delete(self, request, pk=None):
        try:
            campaign = CampaignModel.objects.filter(id=pk).first()
            if not campaign:
                return Response({
                    "status": False, "message": "campaign not found"
                    },status=status.HTTP_404_NOT_FOUND)
            campaign.delete()
            return Response({
                "status": True,
                "message": "Campaign deleted successfully"
                },status=status.HTTP_200_OK)
        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @action(detail=False, methods=['PATCH'], permission_classes=[UserGeneralAuthorization])
    def campaign_update(self, request):
        try:
            campaign_id = request.data.get('id')
            campaign = CampaignModel.objects.filter(id=campaign_id).first()
            if not campaign:
                return Response(
                    {"status": False, "message": "campaign not found to update it."},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = CampaignCreateSerializer(instance=campaign, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "message": handle_serializer_exception(serializer)
                },status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(
                {   
                "status": True,
                "message": "Campaign updated successfully",
                "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as swr:
            return Response(
                {"status": False, "message": str(swr)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    





