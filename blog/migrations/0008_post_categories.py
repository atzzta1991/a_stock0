# Generated by Django 2.2.7 on 2019-12-18 03:26

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='categories',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='blog.Category'),
        ),
    ]