from django.contrib import admin
from .models import CustomUser,ScannedApp
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('user_type',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# admin.site.register(CustomUser)

# ScannedApp Admin
class ScannedAppAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'package_name', 'user', 'security_score', 'scanned_at')
    search_fields = ('app_name', 'package_name', 'developer', 'user__username')  # Search by app name, package, developer, and user
    list_filter = ('security_score', 'scanned_at')  # Add filtering options
    ordering = ('-scanned_at',)  # Show latest scanned apps first
    readonly_fields = ('scanned_at',)  # Prevent modification of scan timestamps

admin.site.register(ScannedApp, ScannedAppAdmin)