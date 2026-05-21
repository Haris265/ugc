from django.contrib import admin
from authentication.models import UserModel, UserWhitelistTokenModel, ClientProfileModel


# Register your models here.
admin.site.register(UserModel)
admin.site.register(UserWhitelistTokenModel)
admin.site.register(ClientProfileModel)



