from rest_framework import serializers
from .models import *


# Create your serializers here.
class TruckTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TruckType
        fields = '__all__'


class TrackingTransportationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingTransportation
        fields = '__all__'


class TruckRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TruckRequest
        fields = '__all__'


class TruckListSerializer(serializers.ModelSerializer):
    truck_type = TruckTypeSerializer(read_only=True)
    transportation = TrackingTransportationSerializer(read_only=True)

    class Meta:
        model = TruckRequest
        fields = '__all__'


class TruckLoadingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TruckLoadingDetails
        fields = '__all__'
