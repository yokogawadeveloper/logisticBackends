# Generated by Django 4.2.11 on 2024-04-23 04:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleMaster',
            fields=[
                ('module_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('module_name', models.CharField(max_length=100, null=True)),
                ('module_slug', models.CharField(max_length=100, null=True)),
                ('root', models.CharField(max_length=100, null=True)),
                ('m_color', models.CharField(max_length=100, null=True)),
                ('m_icon_name', models.CharField(max_length=100, null=True)),
                ('m_link', models.CharField(max_length=100, null=True)),
                ('menu_flag', models.BooleanField(default=True)),
                ('sort_no', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'ModuleMaster',
            },
        ),
        migrations.CreateModel(
            name='RoleMaster',
            fields=[
                ('role_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('role_name', models.CharField(max_length=30, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'RoleMaster',
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('add_access', models.BooleanField(default=False)),
                ('delete_access', models.BooleanField(default=False)),
                ('view_access', models.BooleanField(default=False)),
                ('edit_access', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('module_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ModuleMasterTable', to='master.modulemaster')),
                ('role_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='RoleMasterTable', to='master.rolemaster')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'UserRole',
            },
        ),
        migrations.CreateModel(
            name='UserAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('emp_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='EmployeeUser', to=settings.AUTH_USER_MODEL)),
                ('role_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='RoleMaster', to='master.rolemaster')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'UserAccess',
            },
        ),
    ]
