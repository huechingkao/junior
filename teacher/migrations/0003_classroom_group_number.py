# Generated by Django 2.1.2 on 2018-10-14 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_auto_20181015_0243'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='group_number',
            field=models.IntegerField(default=4),
        ),
    ]