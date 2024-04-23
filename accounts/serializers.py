from rest_framework import serializers
from .models import Department, SubDepartment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your serializers here.
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class SubDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDepartment
        fields = '__all__'
        depth = 1


class EmployeeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
        depth = 1

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class EmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):
    role = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    subDepartment = serializers.SerializerMethodField()

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
