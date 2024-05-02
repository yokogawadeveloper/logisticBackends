from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from rest_framework import viewsets
from datetime import datetime
from .frames import column_mapping
from .utils import send_email
from workflow.models import *
from .serializers import *
import pandas as pd
import time


# Create your views here.
class DispatchInstructionViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = DispatchInstructionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if 'approverlist' in request.data:
            appover_list_to_app = 0
            appover_current_da_lev_2 = 0
            for val in request.data['approverlist']:
                appover_current_da_lev_1 = val['level']
                if val['required_list']:
                    if appover_current_da_lev_1 != appover_current_da_lev_2:
                        appover_list_to_app += 1
                    for emp_id in val['emp_list']:
                        WorkFlowDaApprovers.objects.create(
                            dil_id_id=serializer.instance.dil_id,
                            wf_id_id=val['wf_id'],
                            approver=val['approval'],
                            level=val['level'],
                            parallel=val['parallel'],
                            emp_id=emp_id,
                            status="pending",
                            created_by=request.user
                        )
                appover_current_da_lev_2 = val['level']
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, url_path='complete_dil')
    def complete_dil(self, request, *args, **kwargs):
        try:
            payload = request.data
            dil_id = payload.get("dil_id")
            data = DispatchInstruction.objects.values().get(dil_id=dil_id)
            if not data:
                return Response({'message': 'DA not found', 'status': status.HTTP_204_NO_CONTENT})

            dil_filter = DispatchInstruction.objects.filter(dil_id=dil_id).values('dil_stage')[0]['dil_stage']
            workflow_da_list = WorkFlowDaApprovers.objects.filter(dil_id_id=dil_id, level=1).values()
            for wf in workflow_da_list:
                DAUserRequestAllocation.objects.create(
                    dil_id_id=dil_id,
                    emp_id_id=wf['emp_id'],
                    status="pending",
                    approver_stage=wf['approver'],
                    approver_level=wf['level'],
                    created_by_id=request.user.id
                )
            # create DAUserRequestAllocation for each approver
            DAAuthThreads.objects.create(
                dil_id_id=dil_id,
                emp_id=request.user.id,
                remarks='DA prepared',
                status="DA Submitted",
                created_by_id=request.user.id
            )
            # update the dil_stage
            DispatchInstruction.objects.filter(dil_id=dil_id).update(
                submitted_date=datetime.now(),
                dil_status_no=1,
                dil_status='DIL Submitted'
            )
            return Response({'message': 'DA completed successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(methods=['post'], detail=False, url_path='dil_list_based_on_status')
    def dil_list_based_on_status(self, request, *args, **kwargs):
        try:
            date_from = request.data['date_from']
            date_to = request.data['date_to']
            dil_status_no = request.data['dil_status_no']
            so_no = request.data['so_no']

            data = DispatchInstruction.objects.filter(
                created_at__range=[date_from, date_to],
                dil_status_no=dil_status_no,
                so_no=so_no
            ).values().order_by('dil_id')
            serializer = DispatchInstructionSerializer(data, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='get_complete_dil_creation_wise')
    def get_complete_dil_creation_wise(self, request):
        try:
            filter_data = User.objects.filter(id=request.user.id)
            filter_data.values('is_department_head', 'department_id', 'is_sub_department_head', 'sub_department_id')
            obj = filter_data[0]
            # check if the user is dept head or sub dept head
            if obj.is_department_head == "Yes":
                ids = User.objects.filter(dept_id=obj.department_id).values_list('id', flat=True)
            elif obj.is_sub_department_head == "Yes":
                ids = User.objects.filter(sub_dept_id=obj.sub_department_id).values_list('id', flat=True)
            else:
                ids = User.objects.filter(id=request.user.id).values_list('id', flat=True)
            # workflow access ids
            wfa_ids = WorkFlowDeptEmp.objects.filter(type="da_view_employee", emp_id=request.user.id)
            wfa_ids = wfa_ids.values_list('wfa_id_id', flat=True)
            wf_ids = WorkFlowAccess.objects.filter(wfa_id__in=wfa_ids).values_list('wf_id_id', flat=True)
            filter_data = DispatchInstruction.objects.filter(wf_type__in=wf_ids)
            # get the da_ids based on the user id
            query_set = self.get_queryset().filter(created_by_id__in=ids).order_by('-dil_id')
            query_set = query_set | filter_data
            query_set = query_set.distinct()
            serializer = self.serializer_class(query_set, many=True, context={'request': request})
            serializer_data = serializer.data
            return Response(serializer_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='get_dil_dynamic_filter')
    def get_dil_dynamic_filter(self, request):
        try:
            data = request.data
            filter_data = DispatchInstruction.objects.filter(**data)
            serializer = DispatchInstructionSerializer(filter_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='send_mail')
    def send_mail(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            dil = DispatchInstruction.objects.filter(dil_id=dil_id).first()
            serializer = DispatchInstructionSerializer(dil)
            # email sending
            subject = 'DA Prepared-Re-Export'
            recipient_list = ['ankul.gautam@yokogawa.com', 'rohit.raj@yokogawa.com']
            cc = ['YIL.Developer4@yokogawa.com', 'ankul.gautam@yokogawa.com']
            context = {'data': serializer.data}
            message = render_to_string("prepare_dil.html", context)
            send_email(subject, message, recipient_list, cc)
            if send_email:
                return Response({'message': 'Mail sent successfully', 'status': status.HTTP_200_OK})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SAPDispatchInstructionViewSet(viewsets.ModelViewSet):
    queryset = DispatchInstruction.objects.all()
    serializer_class = SAPDispatchInstructionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='dil_based_on_delivery')
    def dil_based_on_delivery(self, request, *args, **kwargs):
        try:
            delivery_no = request.data['delivery']
            dil = SAPDispatchInstruction.objects.filter(delivery=delivery_no).all()
            if not dil:
                return Response({'message': 'DIL Not found for this delivery', 'status': status.HTTP_204_NO_CONTENT})
            serializer = SAPDispatchInstructionSerializer(dil, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='sap_dil_upload')
    def dil_upload_transaction(self, request, *args, **kwargs):
        try:
            start_time = time.time()  # Start timing
            file = request.FILES['file']
            df = pd.read_excel(file, sheet_name='Sheet1')

            # Filter DataFrame to keep only required columns
            df = df.rename(columns=column_mapping)
            required_columns = list(column_mapping.values())
            df = df[required_columns]

            # Check if all required columns are present
            missing_columns = [col for col in required_columns if col not in df.columns]
            if not missing_columns:
                objects_to_create = []
                for index, row in df.iterrows():
                    obj = SAPDispatchInstruction(
                        reference_doc=row['Reference Document'],
                        sold_to_party_no=row['Sold-to Party'],
                        sold_to_party_name=row['Sold-to Party Name'],
                        delivery=row['Delivery'],
                        delivery_create_date=row['Delivery Create Date'],
                        delivery_item=row['Delivery Item'],
                        tax_invoice_no=row['Tax Invoice Number (ODN)'],
                        reference_doc_item=row['Reference Document Item'],
                        ms_code=row['MS Code'],
                        sales_quantity=row['Quantity (Sales)'],
                        linkage_no=row['Linkage Number'],
                        sales_office=row['Sales Office'],
                        term_of_payment=row['Terms of Payment'],
                        tax_invoice_date=row['Tax Invoice Date'],

                        material_discription=row['Material Description'],
                        plant=row['Plant'],
                        plant_name=row['Plant Name'],
                        unit_sales=row['Unit (Sales)'],
                        billing_number=row['Billing Number'],
                        billing_create_date=row['Billing Create Date'],
                        currency_type=row['Currency (Sales)'],
                        ship_to_party_no=row['Ship-to party'],
                        ship_to_party_name=row['Ship-to Party Name'],
                        ship_to_country=row['Ship-to Country'],
                        ship_to_postal_code=row['Ship-to Postal Code'],
                        ship_to_city=row['Ship-to City'],
                        ship_to_street=row['Ship-to Street'],
                        ship_to_street_for=row['Ship-to Street4'],
                        insurance_scope=row['Insurance Scope'],
                        sold_to_country=row['Sold-to Country'],
                        sold_to_postal_code=row['Sold-to Postal Code'],
                        sold_to_city=row['Sold-to City'],
                        sold_to_street=row['Sold-to Street'],
                        sold_to_street_for=row['Sold-to Street4'],
                        material_no=row['Material Number'],
                        hs_code=row['HS Code'],
                        hs_code_export=row['HS Code Export'],
                        delivery_quantity=row['Delivery quantity'],
                        unit_delivery=row['Unit (Delivery)'],
                        storage_location=row['Storage Location'],
                        dil_output_date=row['DIL Output Date'],
                        sales_doc_type=row['Sales Document Type'],
                        distribution_channel=row['Distribution Channel'],
                        invoice_item=row['Invoice Item'],
                        tax_invoice_assessable_value=row['Tax Invoice Assessable Value'],
                        tax_invoice_total_tax_value=row['Tax Invoice Total Tax Value'],
                        tax_invoice_total_value=row['Tax Invoice Total Value'],
                        sales_item_price=row['Item Price (Sales)'],
                        packing_status=row['Packing status'],
                        do_item_packed_quantity=row['DO Item Packed Quantity'],
                        packed_unit_quantity=row['Packed Quantity unit'],
                        created_by=request.user
                    )
                    objects_to_create.append(obj)

                # Bulk create objects
                with transaction.atomic():
                    SAPDispatchInstruction.objects.bulk_create(objects_to_create)
                    # Calculate upload time
                    end_time = time.time()
                    upload_time = end_time - start_time
                return Response(
                    {'message': 'File uploaded successfully',
                     'timeComplexity': upload_time,
                     'status': status.HTTP_201_CREATED
                     })
            else:
                return Response(
                    {'message': f'File is missing the following required columns: {", ".join(missing_columns)}',
                     'status': status.HTTP_400_BAD_REQUEST})
        except Exception as e:
            transaction.rollback()
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


class DispatchBillDetailsViewSet(viewsets.ModelViewSet):
    queryset = DispatchBillDetails.objects.all()
    serializer_class = DispatchBillDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='create_bill_details')
    def create_bill_details(self, request, *args, **kwargs):
        try:
            payload = request.data
            with transaction.atomic():
                for item in payload:
                    dil = DispatchInstruction.objects.filter(dil_id=item['dil_id']).first()
                    if not dil:
                        transaction.set_rollback(True)
                        return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
                    if not dil.is_active:
                        transaction.set_rollback(True)
                        return Response({'message': 'DIL is not active', 'status': status.HTTP_204_NO_CONTENT})
                    DispatchBillDetails.objects.create(
                        dil_id=dil,
                        material_description=item['material_discription'],
                        material_no=item['material_no'],
                        ms_code=item['ms_code'],
                        s_loc=item['storage_location'],
                        sap_line_item_no=item['delivery_item'],
                        linkage_no=item['linkage_no'],
                        # group=item['group'],
                        quantity=item['delivery_quantity'],
                        country_of_origin=item['ship_to_country'],
                        # item_status=item['item_status'],
                        # item_status_no=item['item_status_no'],
                        packed_quantity=item['do_item_packed_quantity'],
                        item_price=item['sales_item_price'],
                        # igst=item['igst'],
                        # cgst=item['cgst'],
                        # sgst=item['sgst'],
                        tax_amount=item['tax_invoice_assessable_value'],
                        total_amount=item['tax_invoice_total_tax_value'],
                        total_amount_with_tax=item['tax_invoice_total_value'],
                        created_by=request.user
                    )
                return Response({'message': 'Bill details created successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='create_bill')
    def create_bill(self, request, *args, **kwargs):
        try:
            payload = request.data
            dil_id = payload.get("dil_id")
            item_list = payload.get("item_list", [])
            dil = DispatchInstruction.objects.filter(dil_id=dil_id).first()
            if not dil:
                return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
            for item_data in item_list:
                material_description = item_data.get("material_discription")
                material_no = item_data.get("material_no")
                ms_code = item_data.get("ms_code")
                linkage_no = item_data.get("linkage_no")
                quantity = item_data.get("sales_quantity")
                packed_quantity = item_data.get("packed_quantity")
                item_price = item_data.get("sales_item_price")
                tax_amount = item_data.get("tax_invoice_total_tax_value")
                total_amount = item_data.get("tax_invoice_total_value")
                total_amount_with_tax = total_amount
                # Create DispatchBillDetails instance
                DispatchBillDetails.objects.create(
                    dil_id=dil,
                    material_description=material_description,
                    material_no=material_no,
                    ms_code=ms_code,
                    linkage_no=linkage_no,
                    quantity=quantity,
                    packed_quantity=packed_quantity,
                    item_price=item_price,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    total_amount_with_tax=total_amount_with_tax,
                    created_by=request.user
                )
            return Response({'message': 'Bill created successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create_bills_on_dil')
    def create_bills_on_dil(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            bill_details = DispatchBillDetails.objects.filter(dil_id=dil_id).all()
            if not bill_details:
                return Response({'message': 'Bill Details not found', 'status': status.HTTP_204_NO_CONTENT})
            serializer = DispatchBillDetailsSerializer(bill_details, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='get_bill_details_on_dil')
    def get_bill_details_on_dil(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            bill_details = DispatchBillDetails.objects.filter(dil_id=dil_id).all()
            if not bill_details:
                return Response({'message': 'Bill Details not found', 'status': status.HTTP_204_NO_CONTENT})
            serializer = DispatchBillDetailsSerializer(bill_details, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


class MasterItemListViewSet(viewsets.ModelViewSet):
    queryset = MasterItemList.objects.all()
    serializer_class = MasterItemListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MasterItemList.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = MasterItemList.objects.all().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        dil_no = request.data.get('dil_id')
        dispatch_instruction = DispatchInstruction.objects.filter(dil_id=dil_no).first()

        if not dispatch_instruction:
            return Response({'message': 'dil no does not exist', 'status': status.HTTP_204_NO_CONTENT})

        if not dispatch_instruction.is_active:
            return Response({'message': 'dil no is not active', 'status': status.HTTP_204_NO_CONTENT})

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='list_based_on_dil')
    def list_based_on_dil(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            master_item_list = MasterItemList.objects.filter(dil_id=dil_id).all()
            if not master_item_list:
                return Response({'message': 'Master Item List not found', 'status': status.HTTP_204_NO_CONTENT})
            serializer = MasterItemListSerializer(master_item_list, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='create_master_item_list')
    def create_master_item_list(self, request, *args, **kwargs):
        try:
            payload = request.data
            with transaction.atomic():
                for item in payload:
                    dil = DispatchInstruction.objects.filter(dil_id=item['dil_id']).first()
                    if DispatchInstruction.objects.filter(dil_id=item['dil_id']).exists():
                        MasterItemList.objects.create(
                            dil_id=dil,
                            material_description=item['material_discription'],
                            material_no=item['material_no'],
                            ms_code=item['ms_code'],
                            s_loc=item['storage_location'],
                            plant=item['plant'],
                            linkage_no=item['linkage_no'],
                            quantity=item['delivery_quantity'],
                            country_of_origin=item['ship_to_country'],
                            # serial_no=item['serial_no'],
                            # match_no=item['match_no'],
                            # tag_no=item['tag_no'],
                            # range=item['range'],
                            # customer_po_sl_no=item['customer_po_sl_no'],
                            # customer_po_item_code=item['customer_po_item_code'],
                            # item_status=item['item_status'],
                            # item_status_no=item['item_status_no'],
                            packed_quantity=item['do_item_packed_quantity'],
                            created_by=request.user
                        )
                        return Response(
                            {'message': 'Master item list created successfully', 'status': status.HTTP_201_CREATED})
                    else:
                        return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(detail=False, methods=['post'], url_path='create_master_multi_item')
    def create_master_multi_item_(self, request, *args, **kwargs):
        try:
            payload = request.data
            dil_id = payload.get("dil_id")
            item_list = payload.get("item_list", [])
            dil = DispatchInstruction.objects.filter(dil_id=dil_id).first()
            if not dil:
                return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
            for item_data in item_list:
                material_description = item_data.get("material_discription")
                material_no = item_data.get("material_no")
                ms_code = item_data.get("ms_code")
                linkage_no = item_data.get("linkage_no")
                quantity = item_data.get("sales_quantity")
                packed_quantity = item_data.get("packed_quantity")
                plant = item_data.get("plant")
                storage_location = item_data.get("s_loc")
                # Create DispatchBillDetails instance
                MasterItemList.objects.create(
                    dil_id=dil,
                    material_description=material_description,
                    material_no=material_no,
                    ms_code=ms_code,
                    linkage_no=linkage_no,
                    quantity=quantity,
                    packed_quantity=packed_quantity,
                    plant=plant,
                    s_loc=storage_location,
                    created_by=request.user
                )
            return Response({'message': 'Multi Master List created !', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='verify_store_master_item')
    def verify_store_master_item(self, request, *args, **kwargs):
        try:
            dil_no = request.data['dil_id']
            dil_status = request.data['dil_status']
            dil_status_no = request.data['dil_status_no']
            stature = request.data['status']
            remarks = request.data['remarks']
            item_list = request.data['item_list']
            dil = DispatchInstruction.objects.filter(dil_id=dil_no)
            if dil is None:
                return Response({'message': 'DA not found', 'status': status.HTTP_204_NO_CONTENT})
            if dil.exists():
                if stature == "verified":
                    dil.update(dil_status_no=dil_status_no, dil_status=dil_status)
                    for item in item_list:
                        master = MasterItemList.objects.filter(item_id=item['item_id'])
                        master.update(verified_flag=True, verified_by=request.user.id, verified_at=datetime.now())
                elif stature == "modified":
                    dil.update(dil_status_no=dil_status_no, dil_status=dil_status)
                DAAuthThreads.objects.create(
                    dil_id_id=dil_no,
                    emp_id=request.user.id,
                    remarks=remarks,
                    status=stature,
                    approver='Verifier'
                )
                return Response({'message': 'Store Master Item Verified', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='accept_for_packing')
    def accept_for_packing(self, request, *args, **kwargs):
        try:
            dil_no = request.data['dil_id']
            dil_status = request.data['dil_status']
            dil_status_no = request.data['dil_status_no']
            dil = DispatchInstruction.objects.filter(dil_id=dil_no)
            if dil.exists():
                dil.update(dil_status_no=dil_status_no, dil_status=dil_status)
                DAUserRequestAllocation.objects.create(
                    dil_id_id=dil_no,
                    emp_id_id=request.user.id,
                    status='pending',
                    approve_status='packing_dil',
                    approver_stage='packing',
                )
                DAAuthThreads.objects.create(
                    dil_id_id=dil_no,
                    emp_id=request.user.id,
                    remarks=request.user.name,
                    status='Packing Accepted',
                    approver='Packing Accept'
                )
            return Response({'message': 'Store Master Item Assigned', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='assign_to_issuing_item')
    def assign_to_issuing_item(self, request, *args, **kwargs):
        try:
            dil_no = request.data['dil_id']
            dil_status = request.data['dil_status']
            dil_status_no = request.data['dil_status_no']
            remarks = request.data['remarks']
            stature = request.data['status']
            assign_to = request.data['assign_to']
            dil = DispatchInstruction.objects.filter(dil_id=dil_no)
            if dil.exists():
                dil.update(dil_status_no=dil_status_no, dil_status=dil_status)
                # create the allocation for each user
                for ids in assign_to:
                    user_instance = User.objects.filter(id=ids).first()
                    DAUserRequestAllocation.objects.create(
                        dil_id_id=dil_no,
                        emp_id=user_instance,
                        status='pending',
                        approve_status='stores_item_issue',
                        approver_stage='item_issue',
                    )
                # create the thread for the user
                DAAuthThreads.objects.create(
                    dil_id_id=dil_no,
                    emp_id=request.user.id,
                    remarks=remarks,
                    status=stature,
                    approver='Stores Accept'
                )
            return Response({'message': 'Item Issued & Assign', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='packing_master_item')
    def packing_master_item(self, request, *args, **kwargs):
        try:
            dil_no = request.data['dil_id']
            item_list = request.data['item_list']
            dil = DispatchInstruction.objects.filter(dil_id=dil_no)
            for item in item_list:
                master_item = MasterItemList.objects.filter(item_id=item['item_id']).first()
                master_item_packed_quantity = master_item.packed_quantity or 0
                MasterItemList.objects.filter(item_id=item['item_id']).update(
                    packed_quantity=master_item_packed_quantity + item['packed_quantity']
                )
            return Response({'message': 'Master Item Packed', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='packing_assigment')
    def packing_assigment(self, request, *args, **kwargs):
        try:
            dil_no = request.data['dil_id']
            assign_to = request.data['assign_to']
            dil = DispatchInstruction.objects.filter(dil_id=dil_no)
            if dil.exists():
                for ids in assign_to:
                    user_instance = User.objects.filter(id=ids).first()
                    DAUserRequestAllocation.objects.create(
                        dil_id_id=dil_no,
                        emp_id=user_instance,
                        status='pending',
                        approve_status='packing_dil',
                        approver_stage='packing',
                    )
            return Response({'message': 'Packing Assigned', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MasterItemBatchViewSet(viewsets.ModelViewSet):
    queryset = MasterItemList.objects.all()
    serializer_class = MasterItemBatchSerializer

    # filter based on dil_id
    def get_queryset(self):
        dil_id = self.request.query_params.get('dil_id')
        return MasterItemList.objects.filter(dil_id=dil_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='master_list_based_on_dil')
    def master_list_based_on_dil(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            master_item_list = MasterItemList.objects.filter(dil_id=dil_id).all()
            if not master_item_list:
                return Response({'message': 'Master Item List not found', 'status': status.HTTP_204_NO_CONTENT})
            serializer = MasterItemBatchSerializer(master_item_list, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})


class InlineItemListViewSet(viewsets.ModelViewSet):
    queryset = InlineItemList.objects.all()
    serializer_class = InlineItemListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = InlineItemList.objects.all().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        item_list_id = request.data.get('item_list_id')
        master_item_list = MasterItemList.objects.filter(item_id=item_list_id).first()

        if not master_item_list:
            return Response({'message': 'item list id does not exist', 'status': status.HTTP_204_NO_CONTENT})

        if not master_item_list.is_active:
            return Response({'message': 'item list id is not active', 'status': status.HTTP_204_NO_CONTENT})

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, url_path='create_inline_item')
    def create_inline_item(self, request, *args, **kwargs):
        try:
            payload = request.data
            with transaction.atomic():
                for item in payload:
                    master_items = MasterItemList.objects.filter(linkage_no=item['linkage_no'])
                    for master_item in master_items:
                        InlineItemList.objects.create(
                            master_item=master_item,
                            serial_no=item['serial_no'],
                            tag_no=item['tag_no'],
                            quantity=item['quantity'],
                            status='pending',
                            status_no=1,
                            created_by=request.user
                        )
                return Response({'message': 'Inline Items created successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='dynamic_filter_inline_item')
    def dynamic_filter_inline_item(self, request, *args, **kwargs):
        try:
            data = request.data
            filter_data = InlineItemList.objects.filter(**data)
            serializer = InlineItemListSerializer(filter_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DAUserRequestAllocationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = DAUserRequestAllocation.objects.all()
    serializer_class = DAUserRequestAllocationSerializer

    def get_queryset(self):
        query_set = self.queryset
        return query_set

    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        serializer = self.serializer_class(query_set, many=True, context={'request': request})
        serializer_data = serializer.data
        return Response(serializer_data)

    @action(methods=['post'], detail=False, url_path='user_based_da_list_with_status')
    def user_based_da_list_with_status(self, request):
        try:
            data = request.data
            current_user_id = request.user.id
            col_name = data['col_name']
            # get the da_ids based on the user id
            dil_ids = DAUserRequestAllocation.objects.filter(
                emp_id_id=current_user_id,
                status=data['dil_user_req_status'],
                approve_status=data['approve_status'],
                approver_flag=data['approver_flag']
            ).values_list('dil_id_id', flat=True)

            if data['status'] == "all":
                filter_data = DispatchInstruction.objects.filter(
                    dil_id__in=list(dil_ids),
                    **{col_name: data['col_value']}
                )
            else:
                filter_data = DispatchInstruction.objects.filter(
                    dil_id__in=list(dil_ids),
                    **{col_name: data['col_value']},
                    status=data['status']
                )

            # serialize the data
            serializer = DispatchInstructionSerializer(filter_data, many=True, context={'request': request})
            serializer_data = serializer.data
            return Response(serializer_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='dil_on_user_allocation_dynamic_filter')
    def dil_on_user_allocation_dynamic_filter(self, request):
        try:
            data = request.data
            filter_data = DAUserRequestAllocation.objects.filter(**data).values_list('dil_id_id', flat=True)
            query_set = DispatchInstruction.objects.filter(dil_id__in=list(filter_data))
            serializer = DispatchInstructionSerializer(query_set, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DILAuthThreadsViewSet(viewsets.ModelViewSet):
    queryset = DAAuthThreads.objects.all()
    serializer_class = DAAuthThreadsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = DAAuthThreads.objects.all().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            recipient_list, cc = [], []
            data = request.data.copy()
            user_id = request.user.id
            stature = data['status']
            dil_id = data['dil_id']
            with transaction.atomic():
                dil = DispatchInstruction.objects.select_for_update().filter(dil_id=dil_id)
                if dil.exists():
                    mail_dil = dil.first()
                    mail_dil_serializer = DispatchInstructionSerializer(mail_dil)
                    mail_dil_context = {'data': mail_dil_serializer.data}
                    cc.append(request.user.email)
                    cc.extend(['YIL.Developer4@yokogawa.com', 'ankul.gautam@yokogawa.com'])
                    subject = 'DA Prepared-Re-Export'
                    message = render_to_string("prepare_dil.html", mail_dil_context)

                    current_level = dil.values('current_level')[0]['current_level']
                    dil_level = dil.values('dil_level')[0]['dil_level']
                    wf_approver = WorkFlowDaApprovers.objects.filter(dil_id_id=dil_id, level=current_level)
                    checking = wf_approver.values('approver')[0]['approver']
                    wf_da_count = wf_approver.count()

                    if stature == "modification":
                        dispatch = DispatchInstruction.objects.select_for_update().filter(dil_id=data['da_id'])
                        dispatch.update(current_level=1, status="modification")
                        DAUserRequestAllocation.objects.filter(dil_id_id=data['da_id'], approve_status='Approver',
                                                               approved_date=datetime.now()).delete()
                        WorkFlowDaApprovers.objects.filter(dil_id_id=data['da_id']).update(status="pending")

                    elif stature == "reject":
                        DispatchInstruction.objects.select_for_update().filter(dil_id=data['da_id']).update(
                            current_level=1,
                            status="rejected")
                        allocation = DAUserRequestAllocation.objects.filter(dil_id_id=data['da_id'], emp_id=user_id)
                        allocation.update(status="rejected", approved_date=datetime.now())

                    else:
                        wf_da_status = WorkFlowDaApprovers.objects.filter(emp_id=user_id).values('approver')[0][
                            'approver']
                        data['approver'] = wf_da_status

                        allocation = DAUserRequestAllocation.objects.filter(dil_id_id=dil_id, emp_id=user_id)
                        allocation.update(status="approved", approved_date=datetime.now())
                        DAUserRequestAllocation.objects.filter(dil_id_id=dil_id).update(approver_flag=True)

                        if dil_level >= current_level:
                            wf_approver.filter(emp_id=request.user.id).update(status=stature)

                            if wf_da_count == wf_approver.exclude(parallel=True, status__contains='approved').count():
                                current_level += 1
                                dil.update(
                                    current_level=current_level,
                                    dil_status=wf_da_status + ' ' + 'approved',
                                    dil_status_no=2
                                )
                                flow_approvers = WorkFlowDaApprovers.objects.filter(
                                    dil_id_id=dil_id,
                                    level=current_level
                                ).values()
                                for i in flow_approvers:
                                    DAUserRequestAllocation.objects.create(
                                        dil_id_id=dil_id,
                                        emp_id_id=i['emp_id'],
                                        status="pending",
                                        approver_stage=i['approver'],
                                        approver_level=i['level']
                                    )
                                    user = User.objects.filter(username=i['emp_id']).first()
                                    recipient_list.append(user.email)

                            elif wf_da_count == wf_approver.filter(parallel=True, status__contains='approved').count():
                                current_level += 1
                                dil.update(
                                    current_level=current_level,
                                    status=wf_da_status + ' ' + "approved",
                                    da_status_number=2
                                )
                                flow_approvers = WorkFlowDaApprovers.objects.filter(
                                    dil_id_id=dil_id,
                                    level=current_level
                                ).values()
                                for i in flow_approvers:
                                    DAUserRequestAllocation.objects.create(
                                        dil_id_id=dil_id,
                                        emp_id_id=i['emp_id'],
                                        status="pending"
                                    )
                                    user = User.objects.filter(username=i['emp_id']).first()
                                    recipient_list.append(user.email)

                            if dil_level < current_level:
                                dil.update(approved_flag=True, approved_date=datetime.now(), dil_status_no=3)

                    serializer = DAAuthThreadsSerializer(data=data, context={'request': request})
                    if serializer.is_valid():
                        serializer.save()
                        send_email(subject, message, recipient_list, cc)  # Send email
                        return Response({'message': serializer.data, 'status': status.HTTP_201_CREATED})
                return Response({'message': 'DA not found', 'status': status.HTTP_204_NO_CONTENT})
        except IndexError:
            return Response({'message': 'Index out of range..'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'message': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create_da_auth_thread')
    def create_da_auth_thread(self, request, *args, **kwargs):
        try:
            serializer = DAAuthThreadsSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='get_da_auth_thread')
    def get_da_auth_thread(self, request, *args, **kwargs):
        try:
            dil_id = request.data['dil_id']
            da_auth_thread = DAAuthThreads.objects.filter(dil_id=dil_id).all()
            if not da_auth_thread:
                return Response({'message': 'DA Auth Thread not found', 'status': status.HTTP_204_NO_CONTENT})
            serializer = DAAuthThreadsSerializer(da_auth_thread, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})

    @action(methods=['post'], detail=False, url_path='dil_packing_approved')
    def dil_packing_approved(self, request):
        try:
            data = request.data
            stature = data['status']
            dil_id = data['dil_id']

            if stature == "modification":
                DispatchInstruction.objects.filter(dil_id=dil_id).update(current_level=1, status="modification")
                DAUserRequestAllocation.objects.filter(dil_id_id=dil_id).delete()

                WorkFlowDaApprovers.objects.filter(dil_id_id=dil_id).update(status="pending")
                WorkFlowDaApprovers.objects.create(
                    dil_id_id=dil_id,
                    emp_id=request.user.id,
                    remarks=data['remarks'],
                    status="Sent for Modification"
                )

            elif stature == "reject":
                DispatchInstruction.objects.filter(dil_id=dil_id).update(current_level=1, status="rejected")
                DAUserRequestAllocation.objects.filter(dil_id_id=dil_id, emp_id=request.user.id).update(
                    status="rejected")
                DAAuthThreads.objects.create(
                    dil_id_id=dil_id,
                    emp_id=request.user.id,
                    remarks=data['remarks'],
                    status="Rejected"
                )

            elif stature == "hold":
                DispatchInstruction.objects.filter(dil_id=dil_id).update(status="hold")
                DAAuthThreads.objects.create(
                    dil_id_id=dil_id,
                    emp_id=request.user.id,
                    remarks=data['remarks'],
                    status="Hold")

            else:
                DAAuthThreads.objects.create(
                    da_id_id=data['da_id'],
                    emp_id=request.user.id,
                    remarks=data['remarks'],
                    status="packing acknowledged"
                )
                DispatchInstruction.objects.filter(da_id=data['da_id']).update(
                    packing_approver_flag=True,
                    status="packing acknowledged",
                    da_status_number=4
                )
            return Response({'message': 'DA Packing Approved', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='packing_acknowledged')
    def packing_acknowledged(self, request):
        try:
            dil_no = request.data['dil_id']
            dil_status_no = request.data['dil_status_no']
            dil_status = request.data['dil_status']
            stature = request.data['status']
            remarks = request.data['remarks']
            dil = DispatchInstruction.objects.filter(dil_id=dil_no)
            if dil.exists():
                if stature == "modification":
                    dil.update(dil_status_no=1, dil_status="modification")
                else:
                    dil.update(dil_status_no=dil_status_no, dil_status=dil_status)
                DAAuthThreads.objects.create(
                    dil_id_id=dil_no,
                    emp_id=request.user.id,
                    remarks=remarks,
                    status=dil_status,
                    created_by_id=request.user.id
                )
            else:
                return Response({'message': 'DA not found', 'status': status.HTTP_204_NO_CONTENT})
            return Response({'message': 'DA Packing Acknowledged', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FileTypeViewSet(viewsets.ModelViewSet):
    queryset = FileType.objects.all()
    serializer_class = FileTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MultiFileAttachmentViewSet(viewsets.ModelViewSet):
    queryset = MultiFileAttachment.objects.all()
    serializer_class = MultiFileAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create_multi_file_attachment')
    def create_multi_file_attachment(self, request, *args, **kwargs):
        try:
            payload = request.FILES.getlist('file')
            dil_id = request.data['dil_id']
            file_type = request.data['file_type']
            module_name = request.data['module_name']
            module_id = request.data['module_id']
            with transaction.atomic():
                for file in payload:
                    dil = DispatchInstruction.objects.filter(dil_id=dil_id).first()
                    file_type = FileType.objects.filter(file_type_id=file_type).first()
                    if not dil:
                        transaction.set_rollback(True)
                        return Response({'message': 'DIL not found', 'status': status.HTTP_204_NO_CONTENT})
                    if not file_type:
                        transaction.set_rollback(True)
                        return Response({'message': 'File type not found', 'status': status.HTTP_204_NO_CONTENT})
                    # Create multi file attachment
                    MultiFileAttachment.objects.create(
                        dil_id=dil,
                        file=file,
                        file_type=file_type,
                        module_name=module_name,
                        module_id=module_id,
                    )
                return Response({'message': 'Multiple File uploaded successfully', 'status': status.HTTP_201_CREATED})
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'message': str(e), 'status': status.HTTP_400_BAD_REQUEST})
