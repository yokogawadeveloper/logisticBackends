from packing.serializers import *


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


class ItemPackingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPacking
        fields = '__all__'
        depth = 1


class ItemPackingInlineReportSerializer(serializers.ModelSerializer):
    dispatch = DispatchInstructionSerializer(read_only=True)
    box_details = BoxDetailSerializer(read_only=True)

    class Meta:
        model = ItemPackingInline
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')
