# Generated by Django 4.2.6 on 2023-11-06 11:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blocks', '0014_remove_keypoints_user_keypoints_uploaded_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keypoints',
            name='uploaded_by',
        ),
        migrations.AddField(
            model_name='keypoints',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
