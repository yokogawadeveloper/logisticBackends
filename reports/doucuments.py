from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings
from dispatch.models import *
from dispatch.serializers import *
from packing.models import *
from packing.serializers import *
from xhtml2pdf import pisa
from io import BytesIO
import os


# Create Documents logic here.
class CustomerDocumentsDetailsViewSet(viewsets.ModelViewSet):
    queryset = BoxDetails.objects.all()
    serializer_class = BoxDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['POST'], detail=False, url_path='customer_details_doc')
    def customer_details_doc(self, request, pk=None):
        try:
            box_code = request.data['box_code']
            box_details = BoxDetails.objects.get(box_code=box_code)
            dil_id = box_details.dil_id.dil_id
            box_size = box_details.box_size.box_size_id
            dispatch = DispatchInstruction.objects.get(dil_id=dil_id)
            box = BoxSize.objects.get(box_size_id=box_size)
            response_data = {
                'dil_id': dispatch.dil_id,
                'ship_to_party_name':dispatch.ship_to_party_name,
                'ship_to_address':dispatch.ship_to_address,
                'ship_to_city':dispatch.ship_to_city,
                'ship_to_postal_code':dispatch.ship_to_postal_code,
                'ship_to_country':dispatch.ship_to_country,
                'dil_no': dispatch.dil_no,
                'dil_date': dispatch.dil_date,
                'so_no': dispatch.so_no,
                'po_no': dispatch.po_no,
                'po_date': dispatch.po_date,
                'customer_name':dispatch.customer_name,
                'customer_number':dispatch.customer_number,
                'package_id':box_details.box_code,
                'barcode':box_details.box_code,
                'net_weight':box_details.net_weight,
                'gr_weight':box_details.qa_wetness,
                'box_size':box.box_size
            }
            html_template = get_template('customer_details.html')
            html = html_template.render({'response_data': response_data})
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="dispatch_instruction.pdf"'
                # Save the file
                media_path = os.path.join(settings.MEDIA_ROOT, "documents")
                if not os.path.exists(media_path):
                    os.makedirs(media_path)
                file_path = os.path.join(media_path, "customer_details_{0}.pdf".format(dispatch.dil_no))
                with open(file_path, "wb") as file:
                    file.write(response.getvalue())
                return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
