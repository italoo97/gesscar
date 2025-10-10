from django.db import models
from django.utils import timezone

class PageView(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=512)
    referrer = models.CharField(max_length=512, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    browser = models.CharField(max_length=128, null=True, blank=True)
    os = models.CharField(max_length=128, null=True, blank=True)
    device = models.CharField(max_length=128, null=True, blank=True)
    language = models.CharField(max_length=64, null=True, blank=True)
    session_key = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.user or self.ip_address} - {self.path}"