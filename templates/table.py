from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(request):
    # Create a HttpResponse object and set the PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="table.pdf"'

    # Create a canvas object
    c = canvas.Canvas(response, pagesize=A4)

    # Define the width of the columns
    col_widths = [2 * inch, (A4[0] - 4 * inch), 2 * inch]

    # Sample data for the table with multi-line header
    data = [
        ['Header 1', 'material_description\nmaterial_no', 'Header 3'],
        ['Row 1 Column 1', 'Row 1 Column 2', 'Row 1 Column 3'],
        ['Row 2 Column 1', 'Row 2 Column 2', 'Row 2 Column 3'],
        ['Row 3 Column 1', 'Row 3 Column 2', 'Row 3 Column 3'],
    ]

    # Create the Table object
    table = Table(data, colWidths=col_widths)

    # Add a table style without borders or colors
    style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])
    table.setStyle(style)

    # Calculate the position for the table (centering the table on the page)
    table_width, table_height = table.wrap(0, 0)
    x = (A4[0] - table_width) / 2
    y = A4[1] - table_height - inch

    # Draw the table on the canvas
    table.drawOn(c, x, y)

    # Save the PDF
    c.showPage()
    c.save()

    return response
