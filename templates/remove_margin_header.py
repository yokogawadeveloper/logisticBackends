        def draw_header(canvas, page_number, total_pages):
            canvas.setFont("Helvetica-Bold", 12)
            logo_path = os.path.join(settings.MEDIA_ROOT, "images", "yokogawa_logo.jpg")

            # Setting Y-coordinate close to the top edge
            header_start_y = height - inch

            canvas.drawImage(logo_path, inch, header_start_y, width=150, height=30)
            canvas.drawString(6 * inch, header_start_y + 30, "Packing List")
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
            text_object = canvas.beginText(6 * inch, header_start_y - 15)
            for line in doc_info:
                text_object.textLine(line)
            canvas.drawText(text_object)
            canvas.line(inch, header_start_y - 45, width - inch, header_start_y - 45)

            # Provide the total pages under doc_info section
            page_no_info = f"Page {page_number} of {total_pages}"
            canvas.drawString(6 * inch, header_start_y - 55, page_no_info)