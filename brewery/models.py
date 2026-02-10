from django.db import models
from django.contrib.auth.models import User


class Brewery(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='breweries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Breweries'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
