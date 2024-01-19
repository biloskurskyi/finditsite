"""from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models


class KeyPoints(models.Model):
    image = models.ImageField(upload_to='key_points/')
from django.db import models


class UploadedPhoto(models.Model):
    photo = models.ImageField(upload_to='uploaded_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Photo ID: {self.id}, Uploaded at: {self.uploaded_at}'


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
"""