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
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    taluk = models.ForeignKey(Taluk, on_delete=models.CASCADE)
    pincode = models.ForeignKey(Pincode, on_delete=models.CASCADE)
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
    transportation = models.ForeignKey(TrackingTransportation, null=True, on_delete=models.CASCADE)
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
    status = models.CharField(max_length=50, default='Open')
    loading_remarks = models.CharField(max_length=300, null=True)
    delivered_datetime = models.DateTimeField(null=True)
    loaded_flag = models.BooleanField(default=False)
    loaded_date = models.DateTimeField(null=True)
    tracking_status = models.IntegerField(default=0)
    tracking_flag = models.IntegerField(default=0)
    tracking_date = models.DateTimeField(null=True)
    expected_date = models.DateField(null=True, blank=True)
    # other fields
    created_by = models.ForeignKey(User, related_name='UserTable', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'TruckList'
