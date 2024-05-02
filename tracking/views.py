from rest_framework import permissions
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from packing.models import BoxDetails
from .serializers import *
import datetime


# Create your views here.

class TruckTypeViewSet(viewsets.ModelViewSet):
    queryset = TruckType.objects.all()
    serializer_class = TruckTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TruckType.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TrackingTransportationViewSet(viewsets.ModelViewSet):
    queryset = TrackingTransportation.objects.all()
    serializer_class = TrackingTransportationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrackingTransportation.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TruckRequestViewSet(viewsets.ModelViewSet):
    queryset = TruckRequest.objects.all()
    serializer_class = TruckRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TruckRequest.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TruckListViewSet(viewsets.ModelViewSet):
    queryset = TruckRequest.objects.all()
    serializer_class = TruckListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TruckRequest.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, url_path='create_truck_list')
    def create_truck_list(self, request):
        try:
            with transaction.atomic():
                data = request.data
                truck_list = data.get('truck_list')
                transportation = TrackingTransportation.objects.get(id=data.get('transporter'))
                state = State.objects.get(id=data.get('state'))
                district = District.objects.get(id=data.get('district'))
                taluk = Taluk.objects.get(id=data.get('taluk'))
                pincode = Pincode.objects.get(id=data.get('pincode'))

                truck_request_obj = {
                    'transporter': transportation,
                    'state': state,
                    'district': district,
                    'taluk': taluk,
                    'pincode': pincode,
                    'status': data.get('status'),
                    'remarks': data.get('remarks'),
                    'created_by_id': request.user.id,
                    'updated_by_id': request.user.id
                }
                truck_request = TruckRequest.objects.create(**truck_request_obj)

                for truck_data in truck_list:
                    truck_request_types_list_obj = {
                        'truck_request': truck_request,
                        'transportation': transportation,
                        'truck_count': 1,
                    }
                    truck_request_types_list = TruckRequestTypesList.objects.create(**truck_request_types_list_obj)

                    quantity = truck_data.get('quantity')
                    for i in range(quantity):
                        truck_type = TruckType.objects.get(id=truck_data.get('truck_type'))
                        truck_list_obj = {
                            'truck_type': truck_type,
                            'transportation': transportation,
                            'truck_request': truck_request,
                            'truck_request_types_list': truck_request_types_list,
                            'created_by_id': request.user.id,
                            'updated_by_id': request.user.id
                        }
                        TruckList.objects.create(**truck_list_obj)
                return Response({'message': 'Truck list created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TruckLoadingDetailsViewSet(viewsets.ModelViewSet):
    queryset = TruckLoadingDetails.objects.all()
    serializer_class = TruckLoadingDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TruckLoadingDetails.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, url_path='create_loading_details')
    def create_loading_details(self, request):
        try:
            with transaction.atomic():
                data = request.data
                box_list = data['box_list']
                dil_id = data['dil_id']
                truck_list_id = data['truck_list_id']
                vehicle_no = data['vehicle_no']
                driver_name = data['driver_name']
                driver_no = data['driver_no']
                remarks = data['remarks']
                truck_list = TruckList.objects.filter(id=truck_list_id)
                dispatch = DispatchInstruction.objects.filter(dil_id=dil_id)
                if truck_list.exists():
                    truck_list.update(
                        vehicle_no=vehicle_no,
                        driver_name=driver_name,
                        driver_no=driver_no,
                        loading_remarks=remarks,
                        loaded_flag=True,
                        loaded_date=datetime.datetime.now(),
                        tracking_status=1,
                    )
                    for box in box_list:
                        box_code = box['box_code']
                        truck_loading_details_obj = {
                            'dil_id': dispatch.first(),
                            'truck_list_id': truck_list.first(),
                            'box_code': box_code,
                            'created_by_id': request.user.id,
                            'updated_by_id': request.user.id
                        }
                        TruckLoadingDetails.objects.create(**truck_loading_details_obj)
                        box_details = BoxDetails.objects.filter(box_code=box_code)
                        if box_details.exists():
                            box_details.update(loaded_flag=True, loaded_date=datetime.datetime.now())
                        else:
                            return Response({'error': 'Box code not found'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Truck list not found'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'loading details created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeliveryChallanViewSet(viewsets.ModelViewSet):
    queryset = DeliveryChallan.objects.all()
    serializer_class = DeliveryChallanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryChallan.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, url_path='create_delivery_challan')
    def create_delivery_challan(self, request, *args, **kwargs):
        try:
            data = request.data
            truck_list_id = data.get('truck_list')
            dc_invoice_details = data.get('dc_inv_details')
            truck_list = TruckList.objects.filter(id=truck_list_id).first()
            no_of_boxes = truck_list.no_of_boxes
            if truck_list is not None:
                delivery_challan = DeliveryChallan.objects.create(
                    truck_list=truck_list,
                    e_way_bill_no=data.get('e_way_bill_no'),
                    lrn_no=data.get('lrn_no'),
                    lrn_date=data.get('lrn_date'),
                    no_of_boxes=no_of_boxes,
                    created_by=request.user,
                    updated_by=request.user
                )
                for dc_inv in dc_invoice_details:
                    DCInvoiceDetails.objects.create(
                        delivery_challan=delivery_challan,
                        truck_list=truck_list,
                        bill_no=dc_inv.get('bill_no'),
                        bill_date=dc_inv.get('bill_date'),
                        bill_type=dc_inv.get('bill_type'),
                        bill_amount=dc_inv.get('bill_amount'),
                        created_by=request.user,
                        updated_by=request.user
                    )
                serializer = DeliveryChallanSerializer(delivery_challan)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Truck list not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='dynamic_filter_delivery_challan')
    def dynamic_filter_delivery_challan(self, request):
        try:
            filter_data = request.data['data_filter']
            date_flag = request.data['date_flag']
            date_from = request.data['date_from']
            date_to = request.data['date_to']
            # if date flag is true then filter with date range
            if date_flag:
                delivery_challan = DeliveryChallan.objects.filter(
                    created_at__range=[date_from, date_to], **filter_data)
            else:
                delivery_challan = DeliveryChallan.objects.filter(**filter_data)
            serializer = DeliveryChallanSerializer(delivery_challan, many=True)
            for data in serializer.data:
                truck_loading_details = TruckLoadingDetails.objects.filter(truck_list_id=data['truck_list'])
                truck_loading_details_serializer = TruckLoadingDetailsSerializer(truck_loading_details, many=True)
                data['loading_details'] = truck_loading_details_serializer.data
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
