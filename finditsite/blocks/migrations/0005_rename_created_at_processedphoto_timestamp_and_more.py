# Generated by Django 4.2.6 on 2023-11-04 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blocks', '0004_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='processedphoto',
            old_name='created_at',
            new_name='timestamp',
        ),
        migrations.AlterField(
            model_name='processedphoto',
            name='image',
            field=models.ImageField(upload_to='blocks/images/'),
        ),
    ]
