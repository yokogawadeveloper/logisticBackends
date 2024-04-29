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
