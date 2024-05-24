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

        def draw_header(canvas, page_number, total_pages):
            canvas.setFont("Helvetica-Bold", 12)
            logo_path = os.path.join(settings.MEDIA_ROOT, "images", "yil_logo.jpg")
            header_start_y = height - inch + 20
            canvas.drawImage(logo_path, inch-10, header_start_y, width=150, height=50)
            canvas.drawString(inch * 4, header_start_y + 15, "Packing List")
            canvas.setFont("Helvetica", 10)
            
            company_info = [
                "Yokogawa India Limited",
                "Plot No.96, Electronic City Complex, Hosur Road",
                "Bangalore-560100, India",
                "State Name & Code: Karnataka-29 India",
                "Phone: +91-80-2852-1100",
            ]
            text_object = canvas.beginText(inch, header_start_y - 15)
            for line in company_info:
                text_object.textLine(line)
            canvas.drawText(text_object)

            doc_info = [
                f"DO No: {dil.dil_no}",
                f"DO Date: {dil.dil_date}",
                f"SO No: {dil.so_no}",
                f"PO No: {dil.po_no}",
            ]
            text_object = canvas.beginText(6 * inch, header_start_y)
            for line in doc_info:
                text_object.textLine(line)
            canvas.drawText(text_object)

            # Provide the total pages under doc_info section
            page_no_info = f"Page - {page_number}/{total_pages}"
            canvas.drawString(6 * inch, header_start_y - 55, page_no_info)

            # Draw a line under the header section
            canvas.line(inch, header_start_y - 80, width - inch, header_start_y - 80)

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
            y_position = y_position + 50

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
            draw_header(c, page_number, 0)
            y_position = height - 3 * inch
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