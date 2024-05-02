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
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TruckLoadingDetails
        fields = '__all__'
        depth = 1


class DCInvoiceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DCInvoiceDetails
        fields = '__all__'


class DeliveryChallanSerializer(serializers.ModelSerializer):
    dc_invoice_details = DCInvoiceDetailsSerializer(many=True)

    class Meta:
        model = DeliveryChallan
        fields = ('id', 'truck_list', 'e_way_bill_no', 'lrn_no', 'lrn_date', 'no_of_boxes',
                  'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active',
                  'dc_invoice_details')
