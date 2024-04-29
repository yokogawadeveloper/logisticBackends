from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class TruckType(models.Model):
    truck_type_name = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.truck_type_name

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

    def __str__(self):
        return self.transportation_name

    objects = models.Manager()

    class Meta:
        db_table = 'TrackingTransportation'
