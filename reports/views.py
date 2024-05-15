from rest_framework import viewsets, permissions, status
from dispatch.models import DispatchInstruction, DispatchBillDetails
from dispatch.serializers import DispatchInstructionSerializer
from packing.serializers import BoxDetailSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from packing.models import BoxDetails


# Create your views here.

class DispatchReportViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = DispatchInstructionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['post'], detail=False, url_path='dispatch_report')
    def dispatch_report(self, request, *args, **kwargs):
        try:
            filter_data = request.data['data_filter']
            date_type = request.data['date_type']
            date_flag = request.data['date_flag']
            date_from = request.data['date_from']
            date_to = request.data['date_to']
            if date_flag:
                type_filter = date_type + '__range'
                truck_request = DispatchInstruction.objects.filter(**filter_data).filter(
                    **{type_filter: [date_from, date_to]})
            else:
                truck_request = DispatchInstruction.objects.filter(**filter_data)
            serializer = DispatchInstructionSerializer(truck_request, many=True)
            for data in serializer.data:
                data['no_of_boxes'] = BoxDetails.objects.filter(dil_id=data['dil_id'], main_box=True).count()
                data['packing_cost'] = BoxDetails.objects.filter(dil_id=data['dil_id']).aggregate(total=Sum('price'))[
                    'total']
                data['billing_value'] = \
                    DispatchBillDetails.objects.filter(dil_id=data['dil_id']).aggregate(
                        total=Sum('total_amount_with_tax'))['total']
                data['sap_invoice_amount'] = 0
                data['transportation_cost'] = 0
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BoxDetailsReportViewSet(viewsets.ModelViewSet):
    queryset = BoxDetails.objects.all()
    serializer_class = BoxDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query_set = self.queryset.filter(is_active=True)
        return query_set

    @action(methods=['post'], detail=False, url_path='box_details_report')
    def box_details_report(self, request, *args, **kwargs):
        try:
            filter_data = request.data['data_filter']
            date_type = request.data['date_type']
            date_flag = request.data['date_flag']
            date_from = request.data['date_from']
            date_to = request.data['date_to']
            # Combine filters for DispatchInstruction
            dispatch_filters = {**filter_data}
            if date_flag and date_type != 'box_created_date':
                dispatch_filters[date_type + '__range'] = [date_from, date_to]
            dispatch = DispatchInstruction.objects.filter(**dispatch_filters)
            # Get the box details
            if date_flag and date_type == 'box_created_date':
                box_details = BoxDetails.objects.filter(dil_id__in=dispatch).filter(
                    created_at__range=[date_from, date_to], main_box=True)
            else:
                box_details = BoxDetails.objects.filter(dil_id__in=dispatch, main_box=True)
            # Serialize the data
            serializer = BoxDetailSerializer(box_details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


