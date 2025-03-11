from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings

# Create your models here.

# User model with roles
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('user', 'User'),
       
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='admin')
    


class AppScanSummary(models.Model):
    total_apps_scanned = models.IntegerField(default=0, help_text="Total number of apps scanned")
    threats_detected = models.IntegerField(default=0, help_text="Total threats detected across scans")
    community_reports = models.IntegerField(default=0, help_text="Number of reports from the community")
    

    def __str__(self):
        return f"Scans: {self.total_apps_scanned}, Threats: {self.threats_detected}, Reports: {self.community_reports}"


class SafeAppSummary(models.Model):
    app_name = models.CharField(max_length=255, help_text="Name of the application")
    app_image = models.ImageField(upload_to="images/", help_text="App logo or image")
    last_activity = models.DateTimeField(auto_now=True, help_text="Timestamp of the last activity")

    def time_since_last_activity(self):
        time_difference = now() - self.last_activity
        hours = time_difference.total_seconds() // 3600  # Convert seconds to hours

        if hours < 1:
            return "Just now"
        elif hours == 1:
            return "1 hour ago"
        else:
            return f"{int(hours)} hours ago"

    def __str__(self):
        return f"{self.app_name} - Last Activity: {self.time_since_last_activity()}"
    
class FraudAppSummary(models.Model):
    app_name = models.CharField(max_length=255, help_text="Name of the application")
    app_image = models.ImageField(upload_to="images/", help_text="App logo or image")
    last_activity = models.DateTimeField(auto_now=True, help_text="Timestamp of the last activity")

    def time_since_last_activity(self):
        time_difference = now() - self.last_activity
        hours = time_difference.total_seconds() // 3600  # Convert seconds to hours

        if hours < 1:
            return "Just now"
        elif hours == 1:
            return "1 hour ago"
        else:
            return f"{int(hours)} hours ago"

    def __str__(self):
        return f"{self.app_name} - Last Activity: {self.time_since_last_activity()}"
    
class ScannedApp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to CustomUser
    package_name = models.CharField(max_length=255, unique=True)
    app_name = models.CharField(max_length=255)
    developer = models.CharField(max_length=255)
    icon = models.URLField(blank=True, null=True)
    installs = models.CharField(max_length=100)
    rating = models.CharField(max_length=10, blank=True, null=True)
    version = models.CharField(max_length=100, blank=True, null=True)
    updated = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    security_score = models.IntegerField(default=0)
    scanned_at = models.DateTimeField(auto_now_add=True)  # Timestamp when scanned

    def __str__(self):
        return f"{self.app_name} ({self.package_name}) - {self.user.username}"
