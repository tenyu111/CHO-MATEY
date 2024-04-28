from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Product_Categories
# Register your models here.

admin.site.register(Product_Categories)
