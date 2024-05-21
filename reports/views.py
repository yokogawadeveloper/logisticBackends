from rest_framework import viewsets, permissions, status
from dispatch.models import DispatchInstruction, DispatchBillDetails
from dispatch.serializers import DispatchInstructionSerializer
from packing.serializers import BoxDetailSerializer
from .serializers import ExportPDFDispatchSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.db.models import Sum
from packing.models import BoxDetails
from django.http import HttpResponse
from django.conf import settings
import os


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


class PackingListPDFExport(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = ExportPDFDispatchSerializer
    lookup_field = 'dil_id'

    @action(detail=False, methods=['post'], url_path='packing_list_pdf')
    def packing_list_pdf(self, request):
        dil = DispatchInstruction.objects.get(dil_id=request.data['dil_id'])
        response_data = {
            'dil_id': dil.dil_id,
            'dil_no': dil.dil_no,
            'dil_date': dil.dil_date,
            'so_no': dil.so_no,
            'po_no': dil.po_no,
            'master_list': []
        }
        for master_item in dil.master_list.all():
            master_item_data = {
                'item_id': master_item.item_id,
                'item_no': master_item.item_no,
                'material_description': master_item.material_description,  # corrected field name
                'material_no': master_item.material_no,
                'ms_code': master_item.ms_code,
                'quantity': master_item.quantity,
                'linkage_no': master_item.linkage_no,
                'inline_items': []
            }

            for inline_item in master_item.inline_items.all():
                inline_item_data = {
                    'inline_item_id': inline_item.inline_item_id,
                    'serial_no': inline_item.serial_no,
                    'tag_no': inline_item.tag_no,
                }
                master_item_data['inline_items'].append(inline_item_data)

            response_data['master_list'].append(master_item_data)
        # Create PDF file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="dispatch_instruction.pdf"'
        c = canvas.Canvas(response, pagesize=A4)
        c.setTitle("Sample PDF with Header and Footer")
        width, height = A4

        def draw_header(canvas):
            canvas.setFont("Helvetica-Bold", 12)
            logo_path = os.path.join(settings.MEDIA_ROOT, "dispatch_export", "yokogawa_logo.jpg")
            canvas.drawImage(logo_path, inch, height - inch - 30, width=150, height=30)
            canvas.drawString(6 * inch, height - inch, "Packing List")
            canvas.setFont("Helvetica", 10)
            company_info = [
                "Yokogawa India Limited",
                "Plot No.96, Electronic City Complex, Hosur Road",
                "Bangalore-560100, India",
                "State Name & Code: Karnataka-29 India",
                "Phone: +91-80-2852-1100",
            ]
            text_object = canvas.beginText(inch, height - 2 * inch)
            for line in company_info:
                text_object.textLine(line)
            canvas.drawText(text_object)

            doc_info = [
                f"DO No: {dil.dil_no}",
                f"DO Date: {dil.dil_date}",
                f"SO No: {dil.so_no}",
                f"PO No: {dil.po_no}",
            ]
            text_object = canvas.beginText(6 * inch, height - 2 * inch)
            for line in doc_info:
                text_object.textLine(line)
            canvas.drawText(text_object)
            canvas.line(inch, height - 2.8 * inch, width - inch, height - 2.8 * inch)

        def draw_footer(canvas, page_number):
            canvas.setFont("Helvetica", 10)
            footer_text = f"Page {page_number}"
            canvas.drawString(inch, inch / 2, footer_text)

        def draw_content(canvas, y_position):
            canvas.setFont("Helvetica", 10)
            y_position -= 20

            canvas.drawString(inch, y_position, "Ship To:")
            ship_to_info = [
                "Yokogawa India Limited",
                "Plot No.96, Electronic City Complex",
                "Hosur Road ,Bangalore-560100, India",
                "State Name & Code: Karnataka-29 India",
                "Phone: +91-80-2852-1100",
            ]
            text_object = canvas.beginText(inch, y_position - 15)
            for line in ship_to_info:
                text_object.textLine(line)
            canvas.drawText(text_object)

            canvas.drawString(4 * inch, y_position, "Bill To:")
            text_object = canvas.beginText(4 * inch, y_position - 15)
            for line in ship_to_info:
                text_object.textLine(line)
            canvas.drawText(text_object)

            y_position -= 90
            canvas.line(inch, y_position, width - inch, y_position)

            y_position -= 15
            canvas.drawString(inch, y_position, "Packing Id")
            canvas.drawString(2 * inch, y_position, "Model Description")
            canvas.drawString(5 * inch, y_position, "Quantity/Quantity Unit")

            y_position -= 15
            for item in response_data['master_list']:
                if y_position < inch:
                    canvas.showPage()
                    draw_header(canvas)
                    y_position = height - 3 * inch - 20  # Add extra gap after header on new page
                canvas.drawString(inch, y_position, str(item['item_id']))
                canvas.drawString(2 * inch, y_position, str(item['material_description']))
                canvas.drawString(5 * inch, y_position, str(item['quantity']))

                y_position -= 15
                inline_items = item['inline_items']
                if inline_items:
                    for inline_item in inline_items:
                        if y_position < inch:
                            canvas.showPage()
                            draw_header(canvas)
                            y_position = height - 3 * inch - 20  # Add extra gap after header on new page
                        x_position = 1.5 * inch
                        canvas.drawString(x_position, y_position, f"S/N: {inline_item['serial_no']}")
                        x_position += 1.5 * inch
                        canvas.drawString(x_position, y_position, f"TAG: {inline_item['tag_no']}")
                        y_position -= 15

                canvas.setDash(3, 3)
                canvas.line(inch, y_position, width - inch, y_position)
                canvas.setDash()
                y_position -= 15
            return y_position

        def draw_pdf():
            page_number = 1
            y_position = height - 3 * inch
            draw_header(c)
            y_position = draw_content(c, y_position)
            draw_footer(c, page_number)

            while y_position < inch:
                c.showPage()
                page_number += 1
                draw_header(c)
                y_position = height - 3 * inch
                y_position = draw_content(c, y_position)
                draw_footer(c, page_number)

            c.showPage()

        draw_pdf()
        media_path = os.path.join(settings.MEDIA_ROOT, "dispatch_export")
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        file_path = os.path.join(media_path, "dispatch_instruction_{0}.pdf".format(dil.dil_no))
        c.save()
        with open(file_path, "wb") as file:
            file.write(response.getvalue())

        return response
