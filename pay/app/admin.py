from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ['phone', 'email']  # 리스트


admin.site.register(User, UserAdmin)
admin.site.register(PRODUCT)