from django.contrib import admin

from recognition.models import RecognitionResult


@admin.register(RecognitionResult)
class RecognitionResultAdmin(admin.ModelAdmin):
    list_display = ("user", "mode", "image", "created_at")
    list_filter = ("mode",)
    search_fields = ("user__username",)
    list_per_page = 15
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
