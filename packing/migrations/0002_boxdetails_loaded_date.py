# Generated by Django 4.2.11 on 2024-04-30 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='boxdetails',
            name='loaded_date',
            field=models.DateTimeField(null=True),
        ),
    ]