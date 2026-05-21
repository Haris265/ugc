from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField
)
from rest_framework import serializers

from client.models import (
    CampaignModel
)

class CampaignCreateSerializer(ModelSerializer):
    class Meta:
        model = CampaignModel
        fields = ['title', 'budget', 'category', 'deadline', 'description', 'status']
    
    def create(self, validated_data):
        return CampaignModel.objects.create(**validated_data)


class CampaignViewSerializer(ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CampaignModel
        fields = ['id', 'title', 'budget', 'category', 'deadline', 'description', 'status']
    
    

   




    