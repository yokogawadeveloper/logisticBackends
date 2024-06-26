from rest_framework import viewsets, permissions, status
from django.template.loader import get_template
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from packing.serializers import *
from dispatch.serializers import *
from packing.models import *
from tracking.serializers import *
from .serializers import *
from xhtml2pdf import pisa
from io import BytesIO
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
            main_box = request.data['main_box']
            # Combine filters for DispatchInstruction
            dispatch_filters = {**filter_data}
            if date_flag and date_type != 'box_created_date':
                dispatch_filters[date_type + '__range'] = [date_from, date_to]
            dispatch = DispatchInstruction.objects.filter(**dispatch_filters)
            # Get the box details
            if date_flag and date_type == 'box_created_date':
                box_details = BoxDetails.objects.filter(dil_id__in=dispatch).filter(
                    created_at__range=[date_from, date_to], main_box=main_box)
            else:
                box_details = BoxDetails.objects.filter(dil_id__in=dispatch, main_box=main_box)
            # Serialize the data
            serializer = BoxDetailSerializer(box_details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PackingListPDFExport(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = ExportPDFDispatchSerializer
    lookup_field = 'dil_id'

    @action(detail=False, methods=['post'], url_path='dispatch_instruction_pdf')
    def dispatch_instruction_pdf(self, request):
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
        # Create PDF file
        html_template = get_template('dispatch_export.html')
        html = html_template.render({'response_data': response_data})
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="dispatch_instruction.pdf"'
            # Save the file
            media_path = os.path.join(settings.MEDIA_ROOT, "dispatch_export")
            if not os.path.exists(media_path):
                os.makedirs(media_path)
            file_path = os.path.join(media_path, "dispatch_instruction_{0}.pdf".format(dil.dil_no))
            with open(file_path, "wb") as file:
                file.write(response.getvalue())
            return response
        return HttpResponse("Error rendering PDF", status=400)

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
                'material_description': master_item.material_description,
                'material_no': master_item.material_no,
                'ms_code': master_item.ms_code,
                'quantity': master_item.quantity,
                'linkage_no': master_item.linkage_no,
                'customer_po_sl_no': master_item.customer_po_sl_no,
                'customer_po_item_code': master_item.customer_po_item_code,
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

        # Create a buffer to hold the PDF data
        buffer = BytesIO()

        def draw_header(canvas, page_number, total_pages):
            canvas.setFont("Helvetica-Bold", 12)
            logo_path = os.path.join(settings.MEDIA_ROOT, "images", "yokogawa_logo.jpg")
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

            # provide the total pages under doc_info section
            page_no_info = f"Page {page_number} of {total_pages}"
            canvas.drawString(6 * inch, height - 2.7 * inch, page_no_info)

        def draw_footer(canvas, page_number, total_pages):
            canvas.setFont("Helvetica", 10)
            footer_text = f"Page {page_number} of {total_pages}"
            canvas.drawString(inch, inch / 2, footer_text)

        def draw_wrapped_string(canvas, x, y, text, max_width):
            words = text.split()
            lines = []
            line = ""
            for word in words:
                if canvas.stringWidth(line + word) <= max_width:
                    line += word + " "
                else:
                    lines.append(line.strip())
                    line = word + " "
            lines.append(line.strip())
            for line in lines:
                canvas.drawString(x, y, line)
                y -= 12
            return y

        def draw_content(canvas, y_position, page_number, total_pages):
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

            dispatch_header = [
                'Model Description',
                'MS Code',
                'Linkage No',
                'Customer PO Sl No',
                'Customer Part No',
            ]

            y_position -= 15
            canvas.drawString(inch, y_position, "Packing Id")
            text_object = canvas.beginText(2 * inch, y_position)
            for dil_header in dispatch_header:
                text_object.textLine(dil_header)
            canvas.drawText(text_object)
            canvas.drawString(5 * inch, y_position, "Quantity/Quantity Unit")

            # Draw a line based on the header
            canvas.line(inch, y_position - 10 * 5, width - inch, y_position - 10 * 5)

            y_position -= 20 * 4
            for item in response_data['master_list']:
                if y_position < inch:
                    canvas.showPage()
                    page_number += 1
                    draw_header(canvas, page_number, total_pages)
                    y_position = height - 3 * inch - 20  # Add extra gap after header on new page
                    draw_footer(canvas, page_number, total_pages)

                canvas.drawString(inch, y_position, str(item['item_id']))
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['material_description'], 4 * inch)
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['ms_code'], 4 * inch)
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['linkage_no'], 2 * inch)
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['customer_po_sl_no'], 2 * inch)
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['customer_po_item_code'], 2 * inch)
                canvas.drawString(5 * inch, y_position + 50, str(item['quantity']))

                y_position -= 15
                for inline_item in item['inline_items']:
                    if y_position < inch:
                        canvas.showPage()
                        page_number += 1
                        draw_header(canvas, page_number, total_pages)
                        y_position = height - 3 * inch - 20  # Add extra gap after header on new page
                        draw_footer(canvas, page_number, total_pages)

                    text_object = canvas.beginText(2 * inch, y_position)
                    text_object.textLine(f"S/N= : {inline_item['serial_no']}")
                    text_object.textLine(f"TAG= : {inline_item['tag_no']}")
                    canvas.drawText(text_object)
                    y_position -= 30

                canvas.setDash(3, 3)
                canvas.line(inch, y_position, width - inch, y_position)
                canvas.setDash()
                y_position -= 15

            return y_position, page_number

        # First pass: Create a PDF and count the pages
        temp_buffer = BytesIO()
        c = canvas.Canvas(temp_buffer, pagesize=A4)
        width, height = A4

        def first_pass_pdf():
            page_number = 1
            y_position = height - 3 * inch
            draw_header(c, page_number, 0)  # Total pages is 0 for now
            y_position, page_number = draw_content(c, y_position, page_number, 0)
            draw_footer(c, page_number, 0)

            while y_position < inch:
                c.showPage()
                page_number += 1
                draw_header(c, page_number, 0)  # Total pages is 0 for now
                y_position = height - 3 * inch
                y_position, page_number = draw_content(c, y_position, page_number, 0)
                draw_footer(c, page_number, 0)

            c.save()
            return page_number

        total_pages = first_pass_pdf()

        # Second pass: Create the final PDF with correct page numbers
        c = canvas.Canvas(buffer, pagesize=A4)

        def second_pass_pdf():
            page_number = 1
            y_position = height - 3 * inch
            draw_header(c, page_number, total_pages)
            y_position, page_number = draw_content(c, y_position, page_number, total_pages)
            draw_footer(c, page_number, total_pages)

            while y_position < inch:
                c.showPage()
                page_number += 1
                draw_header(c, page_number, total_pages)
                y_position = height - 3 * inch
                y_position, page_number = draw_content(c, y_position, page_number, total_pages)
                draw_footer(c, page_number, total_pages)

            c.save()

        second_pass_pdf()

        # Send the PDF to the client
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="dispatch_instruction.pdf"'
        response.write(buffer.getvalue())

        # Optionally save the PDF file
        media_path = os.path.join(settings.MEDIA_ROOT, "packing_export")
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        file_path = os.path.join(media_path, "packing_list_{0}.pdf".format(dil.dil_no))
        with open(file_path, "wb") as file:
            file.write(buffer.getvalue())

        return response

    @action(detail=False, methods=['post'], url_path='try_packing_list_pdf')
    def try_packing_list_pdf(self, request):
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
                'material_description': master_item.material_description,
                'material_no': master_item.material_no,
                'ms_code': master_item.ms_code,
                'quantity': master_item.quantity,
                'linkage_no': master_item.linkage_no,
                'customer_po_sl_no': master_item.customer_po_sl_no,
                'customer_po_item_code': master_item.customer_po_item_code,
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

        # Create a buffer to hold the PDF data
        buffer = BytesIO()
        width, height = A4

        def draw_header(canvas, page_number, total_pages):
            canvas.setFont("Helvetica-Bold", 12)
            logo_path = os.path.join(settings.MEDIA_ROOT, "images", "yokogawa_logo.jpg")
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

            page_no_info = f"Page {page_number} of {total_pages}"
            canvas.drawString(6 * inch, height - 2.7 * inch, page_no_info)

        def draw_footer(canvas, page_number, total_pages):
            canvas.setFont("Helvetica", 10)
            footer_text = f"Page {page_number} of {total_pages}"
            canvas.drawString(inch, inch / 2, footer_text)

        def draw_wrapped_string(canvas, x, y, text, max_width):
            words = text.split()
            lines = []
            line = ""
            for word in words:
                if canvas.stringWidth(line + word) <= max_width:
                    line += word + " "
                else:
                    lines.append(line.strip())
                    line = word + " "
            lines.append(line.strip())
            for line in lines:
                canvas.drawString(x, y, line)
                y -= 12
            return y

        def draw_content(canvas, y_position, page_number, total_pages):
            canvas.setFont("Helvetica", 10)
            y_position -= 20

            dispatch_header = [
                'Model Description',
                'MS Code',
                'Linkage No',
                'Customer PO Sl No',
                'Customer Part No',
            ]

            y_position -= 15
            canvas.drawString(inch, y_position, "Packing Id")
            text_object = canvas.beginText(2 * inch, y_position)
            for dil_header in dispatch_header:
                text_object.textLine(dil_header)
            canvas.drawText(text_object)
            canvas.drawString(5 * inch, y_position, "Quantity/Quantity Unit")

            # Draw a line based on the header
            canvas.line(inch, y_position - 10 * 5, width - inch, y_position - 10 * 5)

            y_position -= 20 * 4
            for item in response_data['master_list']:
                if y_position < inch:
                    canvas.showPage()
                    page_number += 1
                    draw_header(canvas, page_number, total_pages)
                    y_position = height - 3 * inch - 20  # Add extra gap after header on new page
                    draw_footer(canvas, page_number, total_pages)

                canvas.drawString(inch, y_position, str(item['item_id']))
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['material_description'], 4 * inch)
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['ms_code'], 4 * inch)
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['linkage_no'], 2 * inch)
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['customer_po_sl_no'], 2 * inch)
                y_position = draw_wrapped_string(canvas, 2 * inch, y_position, item['customer_po_item_code'], 2 * inch)
                canvas.drawString(5 * inch, y_position + 50, str(item['quantity']))

                y_position -= 15
                for inline_item in item['inline_items']:
                    if y_position < inch:
                        canvas.showPage()
                        page_number += 1
                        draw_header(canvas, page_number, total_pages)
                        y_position = height - 3 * inch - 20  # Add extra gap after header on new page
                        draw_footer(canvas, page_number, total_pages)

                    text_object = canvas.beginText(2 * inch, y_position)
                    text_object.textLine(f"S/N= : {inline_item['serial_no']}")
                    text_object.textLine(f"TAG= : {inline_item['tag_no']}")
                    canvas.drawText(text_object)
                    y_position -= 30

                canvas.setDash(3, 3)
                canvas.line(inch, y_position, width - inch, y_position)
                canvas.setDash()
                y_position -= 15

            return y_position, page_number

        # First pass: Create a PDF and count the pages
        temp_buffer = BytesIO()
        c = canvas.Canvas(temp_buffer, pagesize=A4)

        def first_pass_pdf():
            page_number = 1
            y_position = height - 3 * inch
            draw_header(c, page_number, 0)  # Total pages is 0 for now
            y_position, page_number = draw_content(c, y_position, page_number, 0)
            draw_footer(c, page_number, 0)

            while y_position < inch:
                c.showPage()
                page_number += 1
                draw_header(c, page_number, 0)  # Total pages is 0 for now
                y_position = height - 3 * inch
                y_position, page_number = draw_content(c, y_position, page_number, 0)
                draw_footer(c, page_number, 0)

            c.save()
            return page_number

        total_pages = first_pass_pdf()

        # Second pass: Create the final PDF with correct page numbers
        c = canvas.Canvas(buffer, pagesize=A4)

        def second_pass_pdf():
            page_number = 1
            y_position = height - 3 * inch
            draw_header(c, page_number, total_pages)
            y_position, page_number = draw_content(c, y_position, page_number, total_pages)
            draw_footer(c, page_number, total_pages)

            while y_position < inch:
                c.showPage()
                page_number += 1
                draw_header(c, page_number, total_pages)
                y_position = height - 3 * inch
                y_position, page_number = draw_content(c, y_position, page_number, total_pages)
                draw_footer(c, page_number, total_pages)

            c.save()

        second_pass_pdf()

        # Send the PDF to the client
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="dispatch_instruction.pdf"'
        response.write(buffer.getvalue())
        return response


class CustomerConsigneeExport(viewsets.ModelViewSet):
    queryset = TruckLoadingDetails.objects.all()
    serializer_class = TruckLoadingDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query_set = self.queryset.filter(is_active=True)
        return query_set

    @action(methods=['post'], detail=False, url_path='annexure_delivery_challan')
    def annexure_delivery_challan(self, request, *args, **kwargs):
        try:
            loading_details = self.queryset.filter(truck_list_id=request.data['truck_list_id']).values_list('box_code')
            item_packing = ItemPacking.objects.filter(box_code__in=loading_details).values_list('item_ref_id')
            master_list = MasterItemList.objects.filter(item_id__in=item_packing)
            item_serializer = MasterItemListSerializer(master_list, many=True)
            # Delivery Challan
            delivery_challan = DeliveryChallan.objects.filter(truck_list=request.data['truck_list_id'])
            challan_serializer = DeliveryChallanSerializer(delivery_challan, many=True)
            context = {'item_data': item_serializer.data, 'delivery_challan': challan_serializer.data}
            # Create PDF file
            html_template = get_template('annexure_delivery_challan.html')
            html = html_template.render(context)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="annexure_delivery_challan.pdf"'
                media_path = os.path.join(settings.MEDIA_ROOT, "dispatch_export")
                if not os.path.exists(media_path):
                    os.makedirs(media_path)
                file_path = os.path.join(media_path,
                                         "annexure_delivery_challan{0}.pdf".format(request.data['truck_list_id']))
                with open(file_path, "wb") as file:
                    file.write(response.getvalue())
                return response
            return HttpResponse("Error rendering PDF", status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='customer_consignee')
    def customer_consignee(self, request, *args, **kwargs):
        try:
            # Fetch the dispatch instruction, master list and delivery challan
            dispatch = DispatchInstruction.objects.get(dil_id=request.data['dil_id'])
            dispatch_serializer = DispatchInstructionSerializer(dispatch)

            master_list = MasterItemList.objects.filter(dil_id=request.data['dil_id'])
            item_serializer = MasterItemListSerializer(master_list)

            delivery_challan = DeliveryChallan.objects.filter(truck_list__id=request.data['truck_list_id']).first()
            dc_invoice = DCInvoiceDetails.objects.filter(delivery_challan=delivery_challan)
            dc_invoice_serializer = DCInvoiceDetailsSerializer(dc_invoice, many=True)

            context = {
                'dispatch_data': dispatch_serializer.data,
                'master_list': item_serializer.data,
                'dc_invoice_data': dc_invoice_serializer.data
            }
            # Create PDF file
            html_template = get_template('customer_consignee.html')
            html = html_template.render(context)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="customer_consignee.pdf"'
                # Save the file
                media_path = os.path.join(settings.MEDIA_ROOT, "dispatch_export")
                if not os.path.exists(media_path):
                    os.makedirs(media_path)
                file_path = os.path.join(media_path, "customer_consignee{0}.pdf".format(request.data['dil_id']))
                with open(file_path, "wb") as file:
                    file.write(response.getvalue())
                return response
            return HttpResponse("Error rendering PDF", status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# create report part views here.
class ItemPackingReportViewSet(viewsets.ModelViewSet):
    queryset = ItemPacking.objects.all()
    serializer_class = ItemPackingSerializer

    @action(methods=['post'], detail=False, url_path='item_packing_report')
    def item_packing_report(self, request, *args, **kwargs):
        try:
            data = request.data
            dil_flag = data.get('dil_flag', False)
            box_flag = data.get('box_flag', False)
            inline_flag = data.get('inline_flag', False)

            dil_filter = data.get('dil_filter', {})
            box_filter = data.get('box_filter', {})
            inline_filter = data.get('inline_filter', {})

            dispatch_ids = []
            box_codes = []
            inline_query = ItemPackingInline.objects.none()
            dispatch_serializer = None  # Initialize to None

            if dil_flag:
                dispatch_ids = DispatchInstruction.objects.filter(**dil_filter).values_list('dil_id', flat=True)

            if box_flag:
                box_query = BoxDetails.objects.filter(**box_filter)
                if dispatch_ids:
                    box_query = box_query.filter(dil_id__in=dispatch_ids)
                box_serializer = BoxDetailSerializer(box_query, many=True)
                box_codes = [b['box_code'] for b in box_serializer.data]

            if inline_flag:
                inline_query = ItemPackingInline.objects.filter(**inline_filter)

            if box_codes:
                item_packing = ItemPacking.objects.filter(box_code__in=box_codes)
                item_packing_ids = item_packing.values_list('item_packing_id', flat=True)
                if inline_flag:
                    inline_query = inline_query.filter(item_pack_id__in=item_packing_ids)
                else:
                    inline_query = ItemPackingInline.objects.filter(item_pack_id__in=item_packing_ids)

            # Final response for packing inline
            serializer = ItemPackingInlineReportSerializer(inline_query, many=True)
            result = []
            # Binding the box details and dispatch data
            for response in serializer.data:
                if response['box_details']:
                    first_box_detail = response['box_details'][0]
                    dispatch = DispatchInstruction.objects.get(dil_id=first_box_detail['dil_id'])
                    dispatch_serializer = DispatchInstructionSerializer(dispatch)
                response['dispatch'] = dispatch_serializer.data
                result.append(response)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
