from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out
from django.db import models
from django.utils import timezone


class KeyPoints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='photos/')
    added_at = models.DateTimeField(default=timezone.now)
    category_id = models.IntegerField(null=True)

    def __str__(self):
        return str(self.added_at)

    class Meta:
        verbose_name_plural = "Photos info"


class PhotoProcess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50, default='Processing')

    def __str__(self):
        return f'Photo Process for User {self.user}'

    class Meta:
        verbose_name_plural = "Photo Process"


def delete_photo_processes(sender, request, **kwargs):
    user_id = request.user.id

    PhotoProcess.objects.filter(user_id=user_id).delete()


user_logged_out.connect(delete_photo_processes)
