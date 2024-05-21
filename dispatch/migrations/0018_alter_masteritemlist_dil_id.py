# Generated by Django 4.2.11 on 2024-05-21 06:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch', '0017_masteritemlist_unit_of_measurement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masteritemlist',
            name='dil_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='master_list', to='dispatch.dispatchinstruction'),
        ),
    ]