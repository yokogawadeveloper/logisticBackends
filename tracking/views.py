from rest_framework import permissions, viewsets, status
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Loop through each TruckRequest instance and retrieve related TruckRequestTypesList instances
        for truck_request in serializer.data:
            instance = TruckRequest.objects.get(id=truck_request['id'])
            truck_request_types_list = instance.truckrequesttypeslist_set.all()
            truck_request_types_list_serializer = TruckRequestTypesListSerializer(truck_request_types_list, many=True)
            truck_request['truck_request_types_list'] = truck_request_types_list_serializer.data
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

    @action(methods=['post'], detail=False, url_path='dynamic_filter_truck_request')
    def dynamic_filter_truck_request(self, request):
        try:
            filter_data = request.data['data_filter']
            date_flag = request.data['date_flag']
            date_from = request.data['date_from']
            date_to = request.data['date_to']
            if date_flag:
                truck_request = TruckRequest.objects.filter(created_at__range=[date_from, date_to], **filter_data)
            else:
                truck_request = TruckRequest.objects.filter(**filter_data)
            serializer = TruckRequestSerializer(truck_request, many=True)
            for truck_request in serializer.data:
                instance = TruckRequest.objects.get(id=truck_request['id'])
                truck_request_types_list = instance.truckrequesttypeslist_set.all()
                truck_request_types_list_serializer = TruckRequestTypesListSerializer(truck_request_types_list,
                                                                                      many=True)
                truck_request['truck_request_types_list'] = truck_request_types_list_serializer.data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TruckListViewSet(viewsets.ModelViewSet):
    queryset = TruckList.objects.all()
    serializer_class = TruckListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TruckList.objects.filter(is_active=True)

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
                # create truck request
                truck_request = TruckRequest.objects.create(
                    transporter=transportation,
                    state=state,
                    district=district,
                    taluk=taluk,
                    pincode=data.get('pincode'),
                    status=data.get('status'),
                    remarks=data.get('remarks'),
                    created_by=request.user,
                    updated_by=request.user
                )
                for truck_data in truck_list:
                    quantity = truck_data.get('quantity')
                    truck_type = TruckType.objects.get(id=truck_data.get('truck_type'))
                    # create truck request types list
                    truck_request_types_list = TruckRequestTypesList.objects.create(
                        truck_request=truck_request,
                        truck_type=truck_type,
                        truck_count=truck_data.get('quantity')
                    )
                    for i in range(quantity):
                        TruckList.objects.create(
                            truck_type=truck_type,
                            transportation=transportation,
                            truck_request=truck_request,
                            truck_request_types_list=truck_request_types_list,
                            created_by=request.user,
                            updated_by=request.user
                        )
                return Response({'message': 'Truck list created successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='update_truck_list')
    def update_truck_list(self, request):
        try:
            with transaction.atomic():
                data = request.data
                truck_request_id = data.get('id')
                transporter_id = data.get('transporter')
                state = State.objects.get(id=data.get('state'))
                district = District.objects.get(id=data.get('district'))
                taluk = Taluk.objects.get(id=data.get('taluk'))
                truck_list = data.get('truck_list')
                # Main Logic
                transportation = TrackingTransportation.objects.get(id=transporter_id)
                truck_request = TruckRequest.objects.get(id=truck_request_id)
                # delete existing TruckRequestTypesList, TruckList
                TruckRequestTypesList.objects.filter(truck_request=truck_request).delete()
                TruckList.objects.filter(truck_request=truck_request).delete()
                # update truck request
                truck_request.transporter = transportation
                truck_request.state = state
                truck_request.district = district
                truck_request.taluk = taluk
                truck_request.pincode = data.get('pincode')
                truck_request.status = data.get('status')
                truck_request.remarks = data.get('remarks')
                truck_request.updated_by = request.user
                truck_request.save()
                for truck_data in truck_list:
                    quantity = truck_data.get('quantity')
                    truck_type = TruckType.objects.get(id=truck_data.get('truck_type'))
                    # create truck request types list
                    truck_request_types_list = TruckRequestTypesList.objects.create(
                        truck_request=truck_request,
                        truck_type=truck_type,
                        truck_count=truck_data.get('quantity')
                    )
                    for i in range(quantity):
                        TruckList.objects.create(
                            truck_type=truck_type,
                            transportation=transportation,
                            truck_request=truck_request,
                            truck_request_types_list=truck_request_types_list,
                            created_by=request.user,
                            updated_by=request.user
                        )
                return Response({'message': 'Truck list updated successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='dynamic_filter_truck_list')
    def dynamic_filter_truck_list(self, request):
        try:
            filter_data = request.data['data_filter']
            date_flag = request.data['date_flag']
            date_from = request.data['date_from']
            date_to = request.data['date_to']
            if date_flag:
                truck_list = TruckList.objects.filter(created_at__range=[date_from, date_to], **filter_data)
            else:
                truck_list = TruckList.objects.filter(**filter_data)

            serializer = TruckListSerializer(truck_list, many=True)
            for data in serializer.data:
                loading_details = TruckLoadingDetails.objects.filter(truck_list_id=data['id'])
                loading_details_serializer = TruckLoadingDetailsSerializer(loading_details.first(), many=False)

                delivery_challan = DeliveryChallan.objects.filter(truck_list=data['id'])
                delivery_challan_serializer = DeliveryChallanSerializer(delivery_challan.first(), many=False)

                data['delivery_challan'] = delivery_challan_serializer.data
                data['loading_details'] = loading_details_serializer.data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='truck_list_on_dil')
    def truck_list_on_dil(self, request):
        try:
            data = request.data
            truck_list_ids = TruckLoadingDetails.objects.filter(dil_id=data['dil_id']).values_list('truck_list_id', )
            truck_list = TruckList.objects.filter(id__in=truck_list_ids)
            serializer = TruckListSerializer(truck_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='checkout_truck_list')
    def checkout_truck_list(self, request):
        try:
            data = request.data
            truck_list_id = data['truck_list_id']
            truck_list = TruckList.objects.filter(id=truck_list_id)
            if truck_list.exists():
                truck_list.update(
                    check_out=data['check_out'],
                    check_out_remarks=data['check_out_remarks'],
                    check_out_by=request.user
                )
                return Response({'message': 'Truck checked out successfully', 'status': status.HTTP_200_OK})
            else:
                return Response({'error': 'Truck list not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='dynamic_dil_or_truck_list')
    def dynamic_dil_or_truck_list(self, request):
        try:
            dispatch_filter = request.data['dispatch_filter']
            truck_filter = request.data['truck_filter']
            if dispatch_filter and truck_filter:
                dispatch = DispatchInstruction.objects.filter(**dispatch_filter)
                loading = TruckLoadingDetails.objects.filter(dil_id__in=dispatch.values_list('dil_id', flat=True))
                truck_list = TruckList.objects.filter(id__in=loading.values_list('truck_list_id', flat=True),
                                                      **truck_filter)
                serializer = TruckListSerializer(truck_list, many=True)
                for data in serializer.data:
                    loading_details = TruckLoadingDetails.objects.filter(truck_list_id=data['id'])
                    loading_details_serializer = TruckLoadingDetailsSerializer(loading_details.first(), many=False)

                    delivery_challan = DeliveryChallan.objects.filter(truck_list=data['id'])
                    delivery_challan_serializer = DeliveryChallanSerializer(delivery_challan.first(), many=False)

                    data['delivery_challan'] = delivery_challan_serializer.data
                    data['loading_details'] = loading_details_serializer.data
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Dispatch filter or Truck filter is required'},
                                status=status.HTTP_400_BAD_REQUEST)
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
            data = request.data
            box_list = data['box_list']
            dil_id = data['dil_id']
            truck_list_id = data['truck_list_id']
            vehicle_no = data['vehicle_no']
            driver_name = data['driver_name']
            driver_no = data['driver_no']
            remarks = data['remarks']
            with transaction.atomic():
                if data['courier_flag'] is True:
                    truck_request = TruckRequest.objects.create(transporter=data['transporter'])
                    truck_request_type = TruckRequestTypesList.objects.create(truck_request=truck_request,truck_type__id=4, truck_count=1)
                    truck_list = TruckList.objects.create(
                        truck_type__id=4,
                        transportation__id=data['transporter'],
                        truck_request=truck_request,
                        truck_request_types_list=truck_request_type,
                        created_by=request.user, updated_by=request.user
                    )
                    truck_list_id = truck_list.id
                # Main Logic
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
                        tracking_status=2,
                        status='Loaded',
                        no_of_boxes=len(box_list)
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
                    # Update truck list status & Dispatch status
                    dispatch = DispatchInstruction.objects.filter(dil_id=dil_id)
                    dispatch.filter(dil_status_no__in=[11, 12, 13]).update(
                        dil_status_no=14,
                        dil_status='Loaded',
                        loaded_flag=True,
                        loaded_date=datetime.datetime.now()
                    )
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
            truck_list = TruckList.objects.filter(id=truck_list_id)
            truck_loading_details = TruckLoadingDetails.objects.filter(truck_list_id=truck_list_id)
            no_of_boxes = truck_list.first().no_of_boxes if truck_list.exists() else 0
            if truck_list.exists():  # Check if truck_list exists
                lrn_date = datetime.datetime.strptime(data.get('lrn_date'), "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                    "%Y-%m-%d")
                delivery_challan = DeliveryChallan.objects.create(
                    truck_list=truck_list.first(),
                    e_way_bill_no=data.get('e_way_bill_no'),
                    lrn_no=data.get('lrn_no'),
                    lrn_date=lrn_date,  # Assign formatted date
                    no_of_boxes=no_of_boxes,
                    created_by=request.user,
                    updated_by=request.user
                )
                for dc_inv in dc_invoice_details:
                    bill_date = datetime.datetime.strptime(dc_inv.get('bill_date'), "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d")
                    DCInvoiceDetails.objects.create(
                        delivery_challan=delivery_challan,
                        truck_list=truck_list.first(),
                        bill_no=dc_inv.get('bill_no'),
                        bill_date=bill_date,  # Assign formatted date
                        bill_type=dc_inv.get('bill_type'),
                        bill_amount=dc_inv.get('bill_amount'),
                        created_by=request.user,
                        updated_by=request.user
                    )
                serializer = DeliveryChallanSerializer(delivery_challan)
                # Update truck list status & Dispatch status
                truck_list.update(status='DC Created', tracking_status=3)
                dil_ids = truck_loading_details.values_list('dil_id', flat=True).distinct()
                dispatch = DispatchInstruction.objects.filter(dil_id__in=dil_ids)
                dispatch.filter(dil_status_no=14).update(dil_status_no=15)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Truck list not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='update_delivery_challan')
    def update_delivery_challan(self, request, *args, **kwargs):
        try:
            data = request.data
            challan_id = data.get('id')
            truck_list_id = data.get('truck_list')
            dc_invoice_details = data.get('dc_inv_details')
            # Main Logic
            delivery_challan = DeliveryChallan.objects.filter(id=challan_id)
            truck_list = TruckList.objects.filter(id=truck_list_id)
            if delivery_challan.exists():
                delivery_challan.update(
                    truck_list=truck_list.first(),
                    e_way_bill_no=data.get('e_way_bill_no'),
                    lrn_no=data.get('lrn_no'),
                    lrn_date=data.get('lrn_date'),
                    no_of_boxes=truck_list.first().no_of_boxes,
                    updated_by=request.user
                )
                # Delete existing invoice details
                DCInvoiceDetails.objects.filter(delivery_challan=delivery_challan.first()).delete()
                for dc_inv in dc_invoice_details:
                    DCInvoiceDetails.objects.create(
                        delivery_challan=delivery_challan.first(),
                        truck_list=truck_list.first(),
                        bill_no=dc_inv.get('bill_no'),
                        bill_date=dc_inv.get('bill_date'),
                        bill_type=dc_inv.get('bill_type'),
                        bill_amount=dc_inv.get('bill_amount'),
                        created_by=request.user,
                        updated_by=request.user
                    )
                serializer = DeliveryChallanSerializer(delivery_challan.first())
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
            # based on list dispatch details
            for data in serializer.data:
                truck_loading_details = TruckLoadingDetails.objects.filter(truck_list_id=data['truck_list'])
                truck_loading_details_serializer = TruckLoadingDetailsSerializer(truck_loading_details, many=True)
                data['loading_details'] = truck_loading_details_serializer.data
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
