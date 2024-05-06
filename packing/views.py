from django.db import transaction
from django.db.models import Count
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *
from .models import *
import random


# Create your views here.
class BoxTypeViewSet(viewsets.ModelViewSet):
    queryset = BoxType.objects.all()
    serializer_class = BoxTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query_set = self.queryset.filter(is_active=True)
        return query_set

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)


class BoxSizeViewSet(viewsets.ModelViewSet):
    queryset = BoxSize.objects.all()
    serializer_class = BoxSizeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query_set = self.queryset.filter(is_active=True)
        return query_set

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)


class BoxDetailViewSet(viewsets.ModelViewSet):
    queryset = BoxDetails.objects.all()
    serializer_class = BoxDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query_set = self.queryset.filter(is_active=True)
        return query_set

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='create_box_details')
    def create_box_details(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                random_code = random.randint(1000, 9999)
                count = [{'count': 1}]
                data['box_serial_no'] = count[0]['count']
                # check if the box is main box or not
                if self.get_queryset().filter(dil_id=data['dil_id']).exists():
                    count = self.get_queryset().filter(dil_id=data['dil_id'], main_box=True)
                    count = count.values('dil_id_id').annotate(count=Count('dil_id_id'))
                    # check if the box count is present
                    if not count.exists():
                        data['box_serial_no'] = 1
                    else:
                        data['box_serial_no'] += count[0]['count']
                # creating BoxDetails
                dil_id = DispatchInstruction.objects.filter(dil_id=data['dil_id']).first()
                box_size_id = BoxSize.objects.filter(box_size_id=data['box_size']).first()
                packing_price = PackingPrice.objects.filter(box_size_id=data['box_size']).first()
                price = packing_price.price if packing_price else 0
                create_data = {
                    'main_box': True,
                    'height': data['box_height'],
                    'length': data['box_length'],
                    'breadth': data['box_breadth'],
                    'panel_flag': data['panel_flag'],
                    'box_code': 'box-da_' + str(data['dil_id']) + '-' + str(random_code),
                    'parent_box': 'box-da_' + str(data['dil_id']) + '-' + str(random_code),
                    'box_serial_no': data['box_serial_no'],
                    'main_dil_no': data['dil_id'],
                    'status': 'packed',
                    'remarks': data['remarks'],
                    'gross_weight': data['gross_weight'],
                    'net_weight': data['net_weight'],
                    'qa_wetness': data['qa_wetness'],
                    'project_wetness': data['project_wetness'],
                    'box_price': price,
                }
                serializer = BoxDetailSerializer(data=create_data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save(created_by=request.user, dil_id=dil_id, box_size=box_size_id)
                # creating MasterItemList
                update_list = []
                dispatch = DispatchInstruction.objects.filter(dil_id=data['dil_id'])
                dispatch.update(dil_status="packing initiated", dil_status_no=5)
                # previous data
                for index, obj in enumerate(data['box_list']):
                    model_obj = BoxDetails.objects.get(box_details_id=obj['box_details_id'])
                    model_obj.parent_box = 'box-da_' + str(data['dil_id']) + '-' + str(random_code)
                    model_obj.status = 'packed'
                    update_list.append(model_obj)
                # update the BoxDetails
                BoxDetails.objects.bulk_update(update_list, ['parent_box', 'status', 'box_serial_no'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            transaction.rollback()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='filter_packed_box')
    def filter_queryset(self, request, *args, **kwargs):
        data = request.data
        if data['main_box'] == 'ALL':
            filter_data = self.get_queryset()
        else:
            filter_data = self.get_queryset().filter(dil_id=data['dil_id'], main_box=data['main_box'],status=data['status'])
        serializer = BoxDetailSerializer(filter_data, many=True, context={'request': request})
        serialize_data = serializer.data
        return Response({'data': serialize_data})

    @action(methods=['post'], detail=False, url_path='filter_packed_box_merged')
    def filter_packed_box_merged(self, request, *args, **kwargs):
        try:
            data = request.data
            if data['main_box'] == 'ALL':
                filter_data = self.get_queryset()
            elif data['status'] == "all":
                filter_data = self.get_queryset().filter(dil_id=data['dil_id'], main_box=data['main_box'])
            else:
                filter_data = self.get_queryset().filter(
                    dil_id=data['dil_id'],
                    main_box=data['main_box'],
                    status=data['status']
                )
            serializer = BoxDetailSerializer(filter_data, many=True, context={'request': request})
            serialize_data = serializer.data
            # filtering child box count
            for index, obj in enumerate(serialize_data):
                count = BoxDetails.objects.filter(parent_box=obj['box_code'])
                count = count.values('parent_box').annotate(count=Count('parent_box'))
                serialize_data[index]['box_count'] = count[0]['count']
            return Response({'data': serialize_data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='box_details_code_filter')
    def box_details_code_filter(self, request, *args, **kwargs):
        try:
            data = request.data
            filter_data = BoxDetails.objects.filter(parent_box=data['box_code'], main_box=False).values_list('box_code',
                                                                                                             flat=True)
            box_data = BoxDetails.objects.filter(box_code__in=filter_data)
            item_data = ItemPacking.objects.filter(box_code__in=filter_data)
            # serializer for box details
            serializer = BoxDetailSerializer(box_data, many=True, context={'request': request})
            box_serializer_data = serializer.data
            # serializer for item packing
            serializer = ItemPackingSerializer(item_data, many=True, context={'request': request})
            item_serializer_data = serializer.data
            item_list = []
            for box in box_serializer_data:
                for item in item_serializer_data:
                    if box['box_code'] == item['box_code']:
                        item_list.append(item)
                box['item_list'] = item_list
            return Response({'box_data': box_serializer_data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ItemPackingViewSet(viewsets.ModelViewSet):
    queryset = ItemPacking.objects.all()
    serializer_class = ItemPackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query_set = self.queryset.filter(is_active=True)
        return query_set

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path='create_multi_item_packing')
    def create_multi_item_packing(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                random_code = random.randint(1000, 9999)
                # check if the box is main box or not
                box_size = BoxSize.objects.filter(box_size_id=data['box_size']).first()
                dil = DispatchInstruction.objects.filter(dil_id=data['dil_id']).first()
                packing_price = PackingPrice.objects.filter(box_size_id=data['box_size']).first()
                price = packing_price.price if packing_price else 0
                if not dil:
                    return Response({'error': 'Invalid dispatch advice number'}, status=status.HTTP_400_BAD_REQUEST)
                if not box_size:
                    return Response({'error': 'Invalid box Size'}, status=status.HTTP_400_BAD_REQUEST)
                # # check if the box is main box or not
                if data['main_box'] is True:
                    parent_box = 'box-dil_' + str(data['dil_id']) + '-' + str(random_code)
                    stature = 'packed'
                    count = [{'count': 1}]
                    data['box_serial_no'] = count[0]['count']
                    # filter the da_no from the box details
                    if BoxDetails.objects.filter(dil_id=data['dil_id']).exists():
                        count = BoxDetails.objects.filter(dil_id=data['dil_id'], main_box=True)
                        count = count.values('dil_id_id').annotate(count=Count('dil_id_id'))
                        if not count.exists():
                            data['box_serial_no'] = 1
                        else:
                            data['box_serial_no'] += count[0]['count']
                else:
                    parent_box = None
                    stature = 'not_packed'
                    count = [{'count': 1}]
                    data['box_serial_no'] = count[0]['count']
                    # filter the da_no from the box details
                    if BoxDetails.objects.filter(dil_id=data['dil_id']).exists():
                        count = BoxDetails.objects.filter(dil_id=data['dil_id'], main_box=True)
                        count = count.values('dil_id_id').annotate(count=Count('dil_id_id'))
                        if not count.exists():
                            data['box_serial_no'] = 1
                        else:
                            data['box_serial_no'] += count[0]['count']

                # insert the BoxDetails
                BoxDetails.objects.create(
                    dil_id=dil,
                    box_size=box_size,
                    parent_box=parent_box,
                    box_code='box-dil_' + str(data['dil_id']) + '-' + str(random_code),
                    height=data['box_height'],
                    status=stature,
                    length=data['box_length'],
                    breadth=data['box_breadth'],
                    panel_flag=data['panel_flag'],
                    price=data['box_price'],
                    dil_id_id=data['dil_id'],
                    remarks=data['remarks'],
                    main_box=data['main_box'],
                    box_serial_no=data['box_serial_no'],
                    main_dil_no=data['dil_id'],
                    gross_weight=data['gross_weight'],
                    net_weight=data['net_weight'],
                    qa_wetness=data['qa_wetness'],
                    project_wetness=data['project_wetness'],
                    box_price=price,
                    created_by=request.user
                )
                # update the dispatch advice status
                dispatch = DispatchInstruction.objects.filter(dil_id=data['dil_id'])
                dispatch.update(dil_status="packing initiated", dil_status_no=10)
                # creating multiple Item Packing
                for obj in data['item_list']:
                    item_packing = ItemPacking.objects.create(
                        item_ref_id_id=obj['item_id'],
                        item_name=obj['material_description'],
                        item_qty=obj['entered_qty'],
                        is_parent=data['main_box'],
                        box_code='box-dil_' + str(data['dil_id']) + '-' + str(random_code),
                        remarks=obj['remarks'],
                        created_by_id=request.user.id,
                    )
                    for inline_items in obj['inline_items']:
                        inline_item = InlineItemList.objects.filter(inline_item_id=inline_items['inline_item_id']).first()
                        serial_no = inline_items['serial_no']
                        tag_no = inline_items['tag_no']
                        ItemPackingInline.objects.create(
                            item_ref_id=inline_item,
                            item_pack_id=item_packing,
                            serial_no=serial_no,
                            tag_no=tag_no,
                            created_by_id=request.user.id
                        )
                # creating MasterItemList
                update_list = []
                for obj in data['item_list']:
                    item_obj = MasterItemList.objects.get(item_id=obj['item_id'])
                    item_obj.packed_quantity = obj['packed_qty'] + obj['entered_qty']
                    packed_qty = obj['packed_qty'] + obj['entered_qty']
                    if packed_qty == obj['quantity'] and data['main_box'] is True:
                        item_obj.status = "packed"
                        item_obj.packing_flag = 4
                    else:
                        item_obj.status = item_obj.status
                        item_obj.packing_flag = 3
                    # appending latest records
                    update_list.append(item_obj)
                MasterItemList.objects.bulk_update(update_list, ['packed_quantity', 'status', 'packing_flag'])
                # update the dispatch advice status
                master_list = MasterItemList.objects.filter(dil_id=data['dil_id'], packing_flag__lte=3).count()
                if master_list == 0:
                    dispatch.update(dil_status="packed", dil_status_no=11)
                # return serializer data
                query_set = self.queryset.latest('item_packing_id')
                serializer = self.serializer_class(query_set, context={'request': request})
                serializer_data = serializer.data
                return Response({'item_packing': serializer_data, 'box_serial_no': data['box_serial_no']})
        except Exception as e:
            transaction.rollback()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='item_packing_code_filter')
    def item_packing_code_filter(self, request):
        try:
            data = request.data
            filter_data = self.get_queryset().filter(box_code=data['box_code'])
            serializer = self.serializer_class(filter_data, many=True, context={'request': request})
            serializer_data = serializer.data
            return Response({'data': serializer_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
