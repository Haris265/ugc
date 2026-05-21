import uuid
from django.db import models
from authentication.models import (
    UserModel,
    ClientProfileModel
)
from core.choices import CampaignStatusChoices

# Create your models here.

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class CampaignModel(BaseModel):
    client = models.ForeignKey(
        ClientProfileModel, 
        on_delete=models.CASCADE, 
        related_name='campaigns'
    )
    title = models.CharField(
        max_length=255, 
        verbose_name="Campaign Title"
    )
    budget = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        help_text="Budget in INR (₹) as per UI"
    )
    category = models.CharField(
        max_length=255, 
    )
    deadline = models.DateField(
        verbose_name="Deadline",
        db_index=True
    )
    description = models.TextField(
        help_text="Describe your campaign goals..."
    )
    status = models.IntegerField(
        choices=CampaignStatusChoices.choices, 
        default=CampaignStatusChoices.LIVE,
        db_index=True
    )
    
    def __str__(self):
        return f"Campaign Name: {self.title} & Client: {self.client.user.full_name}"
    
    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
        ordering = ['-created_at'] 



        




