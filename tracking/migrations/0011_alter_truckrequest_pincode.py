# Generated by Django 4.2.11 on 2024-05-08 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0010_trucklist_no_of_boxes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='truckrequest',
            name='pincode',
            field=models.IntegerField(),
        ),
    ]
