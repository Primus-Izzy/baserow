"""
API views for batch record operations with transaction support.
"""
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from baserow.api.decorators import validate_body, map_exceptions
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.api.schemas import get_error_schema
from baserow.contrib.database.models import Table
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.api.tables.errors import ERROR_TABLE_DOES_NOT_EXIST
from baserow.contrib.database.api.rows.errors import (
    ERROR_ROW_DOES_NOT_EXIST,
    ERROR_ROW_IDS_NOT_UNIQUE
)
from baserow.core.exceptions import UserNotInGroup
from baserow.contrib.database.table.exceptions import TableDoesNotExist
from baserow.contrib.database.rows.exceptions import RowDoesNotExist

from .serializers import (
    BatchRecordOperationSerializer,
    BatchRecordResponseSerializer,
    BatchOperationResultSerializer
)


class BatchRecordOperationsView(APIView):
    """
    API view for performing batch record operations with transaction support.
    """
    
    @method_decorator(csrf_exempt)
    @validate_body(BatchRecordOperationSerializer)
    @map_exceptions({
        UserNotInGroup: ERROR_USER_NOT_IN_GROUP,
        TableDoesNotExist: ERROR_TABLE_DOES_NOT_EXIST,
        RowDoesNotExist: ERROR_ROW_DOES_NOT_EXIST,
    })
    def post(self, request, data):
        """
        Execute batch record operations with optional transaction support.
        """
        table_id = data['table_id']
        operations = data['operations']
        atomic = data.get('atomic', True)
        
        # Get table and validate permissions
        table = RowHandler().get_table(table_id)
        
        # Check user permissions for the table
        if not table.database.group.has_user(request.user):
            raise UserNotInGroup()
        
        results = []
        successful_operations = 0
        failed_operations = 0
        transaction_id = str(uuid.uuid4()) if atomic else None
        
        def execute_operations():
            nonlocal successful_operations, failed_operations
            
            for index, operation in enumerate(operations):
                result = {
                    'operation_index': index,
                    'operation': operation['operation'],
                    'success': False,
                    'row_id': operation.get('row_id'),
                    'data': None,
                    'error': None
                }
                
                try:
                    if operation['operation'] == 'create':
                        row = RowHandler().create_row_for_table(
                            request.user,
                            table,
                            operation['data']
                        )
                        result.update({
                            'success': True,
                            'row_id': row.id,
                            'data': operation['data']
                        })
                        successful_operations += 1
                        
                    elif operation['operation'] == 'update':
                        row = RowHandler().update_row_by_id(
                            request.user,
                            table,
                            operation['row_id'],
                            operation['data']
                        )
                        result.update({
                            'success': True,
                            'data': operation['data']
                        })
                        successful_operations += 1
                        
                    elif operation['operation'] == 'delete':
                        RowHandler().delete_row_by_id(
                            request.user,
                            table,
                            operation['row_id']
                        )
                        result.update({
                            'success': True
                        })
                        successful_operations += 1
                        
                except Exception as e:
                    result.update({
                        'success': False,
                        'error': str(e)
                    })
                    failed_operations += 1
                    
                    if atomic:
                        # Re-raise exception to trigger rollback
                        raise
                
                results.append(result)
        
        # Execute operations with or without transaction
        if atomic:
            try:
                with transaction.atomic():
                    execute_operations()
            except Exception:
                # All operations failed due to transaction rollback
                successful_operations = 0
                failed_operations = len(operations)
                for result in results:
                    if result['success']:
                        result['success'] = False
                        result['error'] = 'Transaction rolled back due to error'
        else:
            execute_operations()
        
        response_data = {
            'success': failed_operations == 0,
            'total_operations': len(operations),
            'successful_operations': successful_operations,
            'failed_operations': failed_operations,
            'results': results,
            'transaction_id': transaction_id
        }
        
        return Response(
            BatchRecordResponseSerializer(response_data).data,
            status=status.HTTP_200_OK if failed_operations == 0 else status.HTTP_207_MULTI_STATUS
        )