# Generated by Django 2.1.2 on 2018-10-14 09:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_pointhistory_profile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='point',
            new_name='assistant',
        ),
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='creative',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='home_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='like',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='profile',
            name='open_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='reply',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='profile',
            name='visitor_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='work',
            field=models.IntegerField(default=0),
        ),
    ]
