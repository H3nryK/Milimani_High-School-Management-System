# Generated by Django 5.0 on 2024-01-13 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0013_contact_remove_useractivity_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mark',
            name='grade',
            field=models.CharField(default='N/A', max_length=10),
        ),
        migrations.AddField(
            model_name='mark',
            name='remark',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
