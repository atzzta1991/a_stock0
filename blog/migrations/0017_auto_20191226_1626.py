# Generated by Django 2.2.7 on 2019-12-26 16:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_auto_20191226_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(default=uuid.uuid4, unique=True),
        ),
    ]
