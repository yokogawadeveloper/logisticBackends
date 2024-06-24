from dispatch.models import DispatchInstruction
from subordinate.models import *

User = get_user_model()


# Create your models here.
class TruckType(models.Model):
    truck_type_name = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'TruckType'


class TrackingTransportation(models.Model):
    truck_type = models.ForeignKey(TruckType, on_delete=models.CASCADE)
    transportation_name = models.CharField(max_length=100, null=True)
    contact_number = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    # other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'TrackingTransportation'


class TruckRequest(models.Model):
    transporter = models.ForeignKey(TrackingTransportation, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True)
    taluk = models.ForeignKey(Taluk, on_delete=models.CASCADE, null=True)
    pincode = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True)
    remarks = models.TextField(null=True)
    # other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'TruckRequest'


class TruckRequestTypesList(models.Model):
    truck_request = models.ForeignKey(TruckRequest, on_delete=models.CASCADE)
    truck_type = models.ForeignKey(TruckType, related_name='truck_request_type_list', on_delete=models.CASCADE)
    truck_count = models.IntegerField(default=0)
    # other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'TruckRequestTypesList'


class TruckList(models.Model):
    truck_type = models.ForeignKey(TruckType, null=True, on_delete=models.CASCADE)
    transportation = models.ForeignKey(TrackingTransportation, null=True, on_delete=models.CASCADE)
    truck_request = models.ForeignKey(TruckRequest, null=True, on_delete=models.CASCADE)
    truck_request_types_list = models.ForeignKey(TruckRequestTypesList, null=True, on_delete=models.CASCADE)
    vehicle_no = models.CharField(max_length=50, null=True, blank=True)
    driver_name = models.CharField(max_length=50, null=True, blank=True)
    driver_no = models.CharField(max_length=50, null=True, blank=True)
    rating = models.CharField(max_length=20, null=True, blank=True)
    rating_remarks = models.CharField(max_length=200, null=True, blank=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_in_remarks = models.CharField(max_length=500, null=True, blank=True)
    check_out_remarks = models.CharField(max_length=500, null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    check_out_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    gate_pass_no = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='Open')
    loading_remarks = models.CharField(max_length=300, null=True)
    delivered_datetime = models.DateTimeField(null=True)
    loaded_flag = models.BooleanField(default=False)
    loaded_date = models.DateTimeField(null=True)
    tracking_status = models.IntegerField(default=0)
    tracking_flag = models.IntegerField(default=0)
    tracking_date = models.DateTimeField(null=True)
    expected_date = models.DateField(null=True, blank=True)
    no_of_boxes = models.IntegerField(default=0)
    # other fields
    created_by = models.ForeignKey(User, related_name='UserTable', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'TruckList'


class TruckDilMappingDetails(models.Model):
    dil_id = models.ForeignKey(DispatchInstruction, null=True, on_delete=models.CASCADE)
    truck_list_id = models.ForeignKey(TruckList, null=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'TruckDilMappingDetails'


class TruckLoadingDetails(models.Model):
    dil_id = models.ForeignKey(DispatchInstruction, null=True, on_delete=models.CASCADE)
    truck_list_id = models.ForeignKey(TruckList, null=True, on_delete=models.CASCADE)
    box_code = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'TruckLoadingDetails'


class DeliveryChallan(models.Model):
    truck_list = models.ForeignKey(TruckList, on_delete=models.CASCADE)
    e_way_bill_no = models.CharField(max_length=100, null=True)
    lrn_no = models.CharField(max_length=100, null=True)
    lrn_date = models.DateField(null=True, blank=True)
    no_of_boxes = models.IntegerField(default=0)
    description_of_goods = models.CharField(max_length=200, null=True)
    mode_of_delivery = models.CharField(max_length=100, null=True)
    freight_mode = models.CharField(max_length=100, null=True)
    destination = models.CharField(max_length=100, null=True)
    kind_attended = models.CharField(max_length=100, null=True)
    consignee_remakes = models.CharField(max_length=100, null=True)
    remarks = models.TextField(null=True)
    # other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'DeliveryChallan'

    def invoice_details(self):
        return DCInvoiceDetails.objects.filter(delivery_challan=self)


class DCInvoiceDetails(models.Model):
    delivery_challan = models.ForeignKey(DeliveryChallan, related_name='dc_invoice_details', on_delete=models.CASCADE)
    dil_id = models.ForeignKey(DispatchInstruction, null=True, on_delete=models.CASCADE)
    so_no = models.CharField(max_length=100, null=True)
    truck_list = models.ForeignKey(TruckList, on_delete=models.CASCADE)
    bill_no = models.CharField(max_length=100, null=True)
    bill_date = models.DateField(null=True, blank=True)
    bill_type = models.CharField(max_length=100, null=True)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'DCInvoiceDetails'


class InvoiceChequeDetails(models.Model):
    dc_invoice_details = models.ForeignKey(DCInvoiceDetails, related_name='invoice_cheque_details',
                                           on_delete=models.CASCADE)
    cod_cheque_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invoice_no = models.CharField(max_length=100, null=True)
    cheque_no = models.CharField(max_length=100, null=True)
    cod_cheque_received_date = models.DateField(null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True)
    cheque_date = models.DateField(null=True, blank=True)
    cheque_withdrawal_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=100, null=True)
    # other fields
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'InvoiceChequeDetails'
