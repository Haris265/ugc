from django.urls import path, include
from rest_framework.routers import DefaultRouter
from client.views import (
    CampaignViewSet
)

client_router = DefaultRouter()
client_router.register(r'campaign/management', CampaignViewSet, basename='campaign/management')

urlpatterns = [
    path('', include(client_router.urls)),
]

