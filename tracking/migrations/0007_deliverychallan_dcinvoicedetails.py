# Generated by Django 4.2.11 on 2024-05-02 09:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracking', '0006_truckloadingdetails_dil_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryChallan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('e_way_bill_no', models.CharField(max_length=100, null=True)),
                ('lrn_no', models.CharField(max_length=100, null=True)),
                ('lrn_date', models.DateField(blank=True, null=True)),
                ('no_of_boxes', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('truck_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracking.trucklist')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'DeliveryChallan',
            },
        ),
        migrations.CreateModel(
            name='DCInvoiceDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_no', models.CharField(max_length=100, null=True)),
                ('bill_date', models.DateField(blank=True, null=True)),
                ('bill_type', models.CharField(max_length=100, null=True)),
                ('bill_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('delivery_challan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracking.deliverychallan')),
                ('truck_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracking.trucklist')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'DCInvoiceDetails',
            },
        ),
    ]
