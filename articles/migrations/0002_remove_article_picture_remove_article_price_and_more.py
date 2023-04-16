# Generated by Django 4.1.7 on 2023-03-25 23:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='article',
            name='price',
        ),
        migrations.RemoveField(
            model_name='article',
            name='text_saved',
        ),
        migrations.AddField(
            model_name='article',
            name='gist_link',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
