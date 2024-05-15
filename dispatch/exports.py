from django.template.loader import get_template
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework import viewsets
from xhtml2pdf import pisa
from io import BytesIO
from .serializers import *
from .models import *
import os


# ViewSets define the view behavior.

class ExportDispatchViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = DispatchInstructionSerializer

    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='export_dispatch_pdf')
    def export_dispatch_pdf(self, request):
        data = request.data
        dispatch_instruction = DispatchInstruction.objects.get(dil_id=data['dil_id'])
        serializer = DispatchInstructionSerializer(dispatch_instruction)
        master_item_list = MasterItemList.objects.filter(dil_id=dispatch_instruction)
        # for master_item in master_item_list:
        #     master_item_batch_list = MasterItemBatch.objects.filter(mil_id=master_item)
        #     master_item.master_item_batch_list = master_item_batch_list

        template_path = get_template('dispatch_export.html')
        context = {'dispatch_instruction': serializer.data}
        html = template_path.render(context)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), response)
        if not pdf.err:
            media_path = os.path.join(settings.MEDIA_ROOT, "dispatch_export")
            if not os.path.exists(media_path):
                os.makedirs(media_path)
            file_path = os.path.join(media_path, f"dispatch_instruction_{dispatch_instruction.dil_id}.pdf")
            with open(file_path, "wb") as file:
                file.write(response.getvalue())
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return Response(pdf.err, status=status.HTTP_400_BAD_REQUEST)
