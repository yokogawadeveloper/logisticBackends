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
    transporter = TrackingTransportationSerializer()

    class Meta:
        model = TruckRequest
        fields = '__all__'


class TruckRequestTypesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TruckRequestTypesList
        fields = '__all__'


class TruckListSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TruckList
        fields = '__all__'
        depth = 1

    def __init__(self, *args, **kwargs):
        depth = kwargs.get('context', {}).get('depth', 0)
        super().__init__(*args, **kwargs)
        if depth <= 1:
            self.fields.pop('check_out_by')


class TruckLoadingDetailsSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TruckLoadingDetails
        fields = '__all__'
        depth = 1


class DCInvoiceDetailsSerializer(serializers.ModelSerializer):
    lrn_no = serializers.ReadOnlyField(source='delivery_challan.lrn_no')
    e_way_bill_no = serializers.ReadOnlyField(source='delivery_challan.e_way_bill_no')
    truck_no = serializers.ReadOnlyField(source='truck_list.vehicle_no')

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
