from django.contrib import admin

# Register your models here.
from django.contrib import admin
from login.models import SocialAccount

admin.site.register(SocialAccount)
