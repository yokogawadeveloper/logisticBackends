# Generated by Django 4.2.11 on 2024-04-29 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0002_truckrequest_trucklist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trucklist',
            old_name='ratingRemarks',
            new_name='rating_remarks',
        ),
    ]