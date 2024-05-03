from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .serializers import DispatchInstructionSerializer
from .models import DispatchInstruction
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
