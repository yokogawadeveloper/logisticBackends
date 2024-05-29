from rest_framework import serializers
from dispatch.models import *
from tracking.models import *


# Create your serializers here.
class ExportPDFInlineItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InlineItemList
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']


class ExportPDFMasterItemSerializer(serializers.ModelSerializer):
    inline_items = ExportPDFInlineItemListSerializer(many=True, read_only=True)

    class Meta:
        model = MasterItemList
        fields = '__all__'


class ExportPDFDispatchSerializer(serializers.ModelSerializer):
    master_list = ExportPDFMasterItemSerializer(many=True, read_only=True)

    class Meta:
        model = DispatchInstruction
        fields = '__all__'


class ExportPDFDeliveryChallanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryChallan
        fields = '__all__'
