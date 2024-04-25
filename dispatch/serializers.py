from rest_framework import serializers
from .models import *


# Serializers define the API representation.
class DispatchInstructionSerializer(serializers.ModelSerializer):
    dil_no = serializers.CharField(max_length=20, required=True)
    request_by = serializers.CharField(source='request.user.username', read_only=True)
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DispatchInstruction
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']
        depth = 1

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        validated_data['is_active'] = True
        validated_data['dil_stage'] = 1
        validated_data['current_level'] = 1
        return DispatchInstruction.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(DispatchInstructionSerializer, self).update(instance, validated_data)


class SAPDispatchInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SAPDispatchInstruction
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return DispatchInstruction.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(SAPDispatchInstructionSerializer, self).update(instance, validated_data)


class DispatchBillDetailsSerializer(serializers.ModelSerializer):
    dil_id = serializers.PrimaryKeyRelatedField(queryset=DispatchInstruction.objects.all(), required=True)

    class Meta:
        model = DispatchBillDetails
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return DispatchBillDetails.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(DispatchBillDetailsSerializer, self).update(instance, validated_data)


class MasterItemListSerializer(serializers.ModelSerializer):
    material_description = serializers.CharField(max_length=100, required=True)
    material_no = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = MasterItemList
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return MasterItemList.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(MasterItemListSerializer, self).update(instance, validated_data)


class InlineItemListSerializer(serializers.ModelSerializer):
    serial_no = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = InlineItemList
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']


class MasterItemBatchSerializer(serializers.ModelSerializer):
    inline_items = InlineItemListSerializer(many=True)

    class Meta:
        model = MasterItemList
        fields = ('item_id', 'dil_id', 'material_description', 'material_no', 'ms_code',
                  's_loc', 'bin', 'plant', 'linkage_no', 'group', 'quantity', 'serial_no',
                  'match_no', 'tag_no', 'range', 'item_status', 'item_status_no', 'inline_items'
                  )


class DAUserRequestAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DAUserRequestAllocation
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return DAUserRequestAllocation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(DAUserRequestAllocationSerializer, self).update(instance=instance, validated_data=validated_data)


class DAAuthThreadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DAAuthThreads
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        # take user id as integer and assign to emp_id
        validated_data['emp_id'] = self.context['request'].user.id
        return DAAuthThreads.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.da_id = validated_data.get('da_id', instance.da_id)
        instance.wf_id = validated_data.get('wf_id', instance.wf_id)
        return super(DAAuthThreadsSerializer, self).update(instance=instance, validated_data=validated_data)


class FileTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileType
        fields = '__all__'

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return FileType.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.file_type = validated_data.get('file_type', instance.file_type)
        instance.updated_by = self.context['request'].user
        return super(FileTypeSerializer, self).update(instance=instance, validated_data=validated_data)


class MultiFileAttachmentSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MultiFileAttachment
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['is_active'] = True
        return MultiFileAttachment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.file_name = validated_data.get('file_name', instance.file_name)
        instance.file_type = validated_data.get('file_type', instance.file_type)
        instance.updated_by = self.context['request'].user
        return super(MultiFileAttachmentSerializer, self).update(instance=instance, validated_data=validated_data)
