# Generated by Django 5.0 on 2024-01-14 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0016_remove_classteacher_selection_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classteacher',
            name='selection',
            field=models.ManyToManyField(to='portal.classsubject'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='selection',
            field=models.ManyToManyField(to='portal.classsubject'),
        ),
    ]
