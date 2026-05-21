import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.validators import FileExtensionValidator
from core.choices import (
    IndustryChoices,
    CompanySizeChoices
)


# Create your models here.

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserModel.Role.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)
        
        
class UserModel(AbstractUser):
    
    class Role(models.IntegerChoices):
        SUPER_ADMIN = 0, 'Super Admin'         
        CLIENT = 1, 'Client' 
        CREATOR = 2, 'Creator'
                        
    username = None  # Remove username
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=50, blank=type, null=True, verbose_name="Full Name")
    phone_no = models.CharField(max_length=12, blank=type, null=True, verbose_name="Phone Number")    
    email = models.CharField(max_length=255, unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=255, verbose_name="Password")
    role = models.IntegerField(choices=Role.choices, default=Role.CLIENT, verbose_name="Role Name")
    is_active = models.BooleanField(default=True)
    otp = models.IntegerField(blank=True, null=True)
    otp_status = models.BooleanField(default=False)
    otp_count = models.IntegerField(default=0)    
    image = models.ImageField(
        upload_to='profile/image/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Profile Image", default="/profile/image/1.jpg"
    )
    def save(self, *args, **kwargs):
        """Password is hashed before saving"""
        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
        
    
    def __str__(self):
            return self.email
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class ClientProfileModel(BaseModel):
    user = models.OneToOneField(
        UserModel, 
        on_delete=models.CASCADE, 
        related_name='brand_profile'
    )
    company_name = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=12)
    industry = models.IntegerField(
        choices=IndustryChoices.choices, 
        blank=True, 
        null=True
    )
    company_size = models.IntegerField(
        choices=CompanySizeChoices.choices, 
        blank=True, 
        null=True
    )
    brand_description = models.TextField(blank=True, null=True)
    website_url = models.URLField(max_length=500, blank=True, null=True)
    instagram_url = models.URLField(max_length=500, blank=True, null=True)
    linkedin_url = models.URLField(max_length=500, blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    pan_number = models.CharField(max_length=50, blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    is_verified = models.BooleanField(
        default=False, 
        help_text="Indicates if the brand has the Verified badge"
    )
    
    def __str__(self):
        return f"Brand Profile: {self.user.email}"
    
    @property
    def total_orders(self):
        return self.client_orders.count()

    @property
    def creators_hired(self):
        return self.client_orders.values('creator').distinct().count()
    
    class Meta:
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"
        ordering = ["user"]
        
        
        
class UserWhitelistTokenModel(models.Model):
    """Model representing hashed whitelist tokens for user authentication"""
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="whitelist_tokens", blank=True, null=True)
    token_fingerprint = models.CharField(blank=False,null=False,default="e99a18c428cb38d5f",max_length=64, unique=True, verbose_name="Token Fingerprint")
    refresh_token_fingerprint = models.CharField(blank=False,null=False,default="e99a18c428cb38d5f",max_length=64, unique=True, verbose_name="Refresh Token Fingerprint")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Token for {self.user.email}"  

    class Meta:
        verbose_name = "User Whitelist Token"
        verbose_name_plural = "User Whitelist Tokens"
        ordering = ["user"]
        




