# Generated by Django 2.2.7 on 2019-12-22 07:59

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('wagtailforms', '0003_capitalizeverbose'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('home', '0002_auto_20191217_1132'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Home',
            new_name='HomeIndex',
        ),
    ]
