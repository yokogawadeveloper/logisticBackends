# Generated by Django 4.2.11 on 2024-05-29 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch', '0018_alter_masteritemlist_dil_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='dispatchinstruction',
            name='bill_to_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dispatchinstruction',
            name='bill_to_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='dispatchinstruction',
            name='bill_to_country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='dispatchinstruction',
            name='bill_to_party_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='dispatchinstruction',
            name='bill_to_party_no',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='dispatchinstruction',
            name='bill_to_postal_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
