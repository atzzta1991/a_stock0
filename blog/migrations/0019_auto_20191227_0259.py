# Generated by Django 2.2.7 on 2019-12-27 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0018_auto_20191227_0255'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='nickname',
            new_name='nick_name',
        ),
    ]
