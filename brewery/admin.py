from django.contrib import admin
from .models import Brewery


@admin.register(Brewery)
class BreweryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('name', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
