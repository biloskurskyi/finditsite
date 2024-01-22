from django.contrib import admin
from .models import KeyPoints, PhotoProcess


@admin.register(KeyPoints)
class KeyPointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'added_at', 'category_id')
    search_fields = ('category_id', )
    list_per_page = 15
    readonly_fields = ('image', 'category_id',)
    ordering = ('-added_at',)


@admin.register(PhotoProcess)
class PhotoProcessAdmin(admin.ModelAdmin):
    list_display = ('user', 'status')
    search_fields = ('status',)
    readonly_fields = ('status',)
    list_per_page = 15
    ordering = ('status',)
