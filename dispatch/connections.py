from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.db.models import F
from .serializers import *
from .models import *
import pyodbc


# ViewSets define the view behavior.

class ConnectionDispatchViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = DispatchInstructionSerializer

    @action(detail=False, methods=['get'], url_path='dump_dispatch')
    def dump_dispatch(self, request, pk=None):
        try:
            server = '10.29.15.169'
            database = 'Logisticks070224'
            username = 'sa'
            password = 'Yokogawa@12345'
            # Establish connection
            connection = pyodbc.connect(
                'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
            connection_cursor = connection.cursor()
            # Execute query
            query = 'SELECT PONO,PODate,PaymentomText,WarrantyPeriod FROM WA_SaleOrderMaster WHERE SoNo = 2008728126'
            connection_cursor.execute(query)
            results = connection_cursor.fetchall()
            # Format results
            data = [
                {'PONO': row.PONO,
                 'PODate': row.PODate,
                 'Payment Terms': row.PaymentomText,
                 'Warranty Period': row.WarrantyPeriod
                 } for row in results]
            connection_cursor.close()
            connection.close()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='external_db')
    def external_db(self, request, pk=None):
        so_no = request.data.get('so_no')
        try:
            server = '10.29.15.169'
            database = 'Logisticks070224'
            username = 'sa'
            password = 'Yokogawa@12345'
            # Establish connection
            connection = pyodbc.connect(
                'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
            connection_cursor = connection.cursor()
            # Fetch item numbers based on so_no
            item_nos_query = MasterItemList.objects.filter(so_no=so_no).values_list('item_no', flat=True)
            item_nos = list(item_nos_query)

            # Construct SQL query with parameters
            query = """
                WITH MaxSoIdCTE AS (
                    SELECT MAX(SoId) AS MaxSoId 
                    FROM WA_SaleOrderMaster 
                    WHERE SoNo = ?
                ) 
                SELECT IT.*, IP.* 
                FROM WA_ItemTable AS IT 
                JOIN MaxSoIdCTE ON IT.SoId = MaxSoIdCTE.MaxSoId 
                JOIN WA_ItemParameter AS IP ON IT.ItemId = IP.ItemId 
                WHERE IT.ItemNo IN ({})
            """.format(', '.join(['?'] * len(item_nos)))

            # Execute query with parameters
            connection_cursor.execute(query, [so_no] + item_nos)
            results = connection_cursor.fetchall()
            json_results = [dict(zip([column[0] for column in connection_cursor.description], row)) for row in results]
            for item in json_results:
                master_item = MasterItemList.objects.filter(item_no=item['ItemNo'], so_no=so_no)
                previous_serial_no_qty = master_item.first().serial_no_qty
                master_item.update(
                    warranty_date=item['WarrantyDate'],
                    warranty_flag=True,
                    customer_po_sl_no=item['Customer PO Sl. No'],
                    customer_po_item_code=item['Customer Part No'],
                    serial_no_qty=previous_serial_no_qty + 1,
                    custom_po_flag=True
                )
                # Create & Delete new InlineItemList records
                InlineItemList.objects.filter(master_item=master_item.first()).delete()
                InlineItemList.objects.create(
                    master_item=master_item.first(),
                    serial_no=item['Serialnumber'],
                    tag_no=item['TagNo'],
                    quantity=1
                )
                # update master item list
            # update Master Item List
            master_lists = MasterItemList.objects.filter(so_no=so_no,quantity=F('serial_no_qty'),serial_flag=False)
            master_lists.update(serial_flag=True)
            connection.commit()
            connection_cursor.close()
            connection.close()
            return Response(json_results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
