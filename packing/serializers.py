from rest_framework import serializers
from .models import *


# Create your serializers here.
class BoxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxType
        fields = '__all__'

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        box_type = BoxType.objects.create(**validated_data)
        return box_type

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        instance.box_type = validated_data.get('box_type', instance.box_type)
        instance.save()
        return instance


class BoxSizeSerializer(serializers.ModelSerializer):
    box_type = BoxTypeSerializer(source='box_type_id', read_only=True)

    class Meta:
        model = BoxSize
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super(BoxSizeSerializer, self).create(validated_data=validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(BoxSizeSerializer, self).update(instance=instance, validated_data=validated_data)


class BoxDetailSerializer(serializers.ModelSerializer):
    box_size = BoxSizeSerializer(source='box_size_id', read_only=True)

    class Meta:
        model = BoxDetails
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')
        # depth = 1

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super(BoxDetailSerializer, self).create(validated_data=validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(BoxDetailSerializer, self).update(instance=instance, validated_data=validated_data)


class ItemPackingSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = ItemPacking
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')
        depth = 1

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super(ItemPackingSerializer, self).create(validated_data=validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super(ItemPackingSerializer, self).update(instance=instance, validated_data=validated_data)
