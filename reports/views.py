from rest_framework import viewsets, permissions, status
from dispatch.models import DispatchInstruction, DispatchBillDetails
from dispatch.serializers import DispatchInstructionSerializer
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
