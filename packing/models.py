from django.db import models
from dispatch.models import DispatchInstruction, MasterItemList
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class BoxType(models.Model):
    box_type_id = models.AutoField(primary_key=True, unique=True)
    box_type = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = "BoxType"


class BoxSize(models.Model):
    box_size_id = models.AutoField(primary_key=True, unique=True)
    box_type = models.ForeignKey(BoxType, null=True, on_delete=models.CASCADE)

    box_size = models.CharField(max_length=500, null=True, blank=True)
    box_description = models.CharField(max_length=500, null=True, blank=True)
    # other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    class Meta:
        db_table = "BoxSize"


class BoxDetails(models.Model):
    box_details_id = models.AutoField(primary_key=True, unique=True)
    dil_id = models.ForeignKey(DispatchInstruction, related_name='dispatch', null=True, on_delete=models.CASCADE)
    box_type = models.ForeignKey(BoxType, related_name='box_types', null=True, on_delete=models.CASCADE)
    box_size = models.ForeignKey(BoxSize, related_name='box_sizes', null=True, on_delete=models.CASCADE)
    box_code = models.CharField(max_length=300, null=True, blank=True)
    parent_box = models.CharField(max_length=300, null=True, blank=True)
    height = models.FloatField(default=0.00, null=True, blank=True)
    length = models.FloatField(default=0.00, null=True, blank=True)
    breadth = models.FloatField(default=0.00, null=True, blank=True)
    price = models.FloatField(default=0.00, null=True, blank=True)
    remarks = models.CharField(max_length=300, null=True, blank=True)
    main_box = models.BooleanField(default=False)
    status = models.CharField(max_length=300, null=True, blank=True)
    box_serial_no = models.IntegerField(null=True)
    main_dil_no = models.IntegerField(null=True)
    loaded_flag = models.BooleanField(default=False)
    delivery_flag = models.BooleanField(default=False)
    panel_flag = models.BooleanField(null=True)
    gross_weight = models.IntegerField(null=True)
    net_weight = models.IntegerField(null=True)
    qa_wetness = models.IntegerField(null=True)
    project_wetness = models.IntegerField(null=True)
    box_price = models.FloatField(default=0.00, null=True, blank=True)
    # Other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = "BoxDetails"


class ItemPacking(models.Model):
    item_packing_id = models.AutoField(primary_key=True, unique=True)
    item_ref_id = models.ForeignKey(MasterItemList, related_name='master_list', null=True, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=1000, null=True, blank=True)
    item_qty = models.IntegerField(null=True, blank=True)
    is_parent = models.BooleanField(default=False)
    box_code = models.CharField(max_length=300, null=True, blank=True)
    remarks = models.CharField(max_length=300, null=True, blank=True)
    sub_item_ref = models.IntegerField(null=True, blank=True)
    serial_no = models.CharField(max_length=300, null=True, blank=True)
    # Other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    class Meta:
        db_table = "ItemPacking"
