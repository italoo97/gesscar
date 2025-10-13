from django.contrib import admin
from .models import Profile, Contact

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'surname', 'email', 'phone']

@admin.register(Contact)
class ProfileContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'whatsapp', 'enterprise', 'instagram', 'website']