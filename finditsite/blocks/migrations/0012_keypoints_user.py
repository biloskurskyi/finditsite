# Generated by Django 4.2.6 on 2023-11-06 10:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blocks', '0011_keypoints_added_at_alter_keypoints_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='keypoints',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
