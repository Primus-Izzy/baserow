"""
Serializers for batch record operations with transaction support.
"""
from rest_framework import serializers
from django.db import transaction
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.api.rows.serializers import RowSerializer
from baserow.contrib.database.models import Table


class BatchOperationSerializer(serializers.Serializer):
    """Base serializer for batch operations."""
    operation = serializers.ChoiceField(choices=['create', 'update', 'delete'])
    row_id = serializers.IntegerField(required=False, allow_null=True)
    data = serializers.JSONField(required=False, default=dict)


class BatchRecordOperationSerializer(serializers.Serializer):
    """Serializer for batch record operations."""
    table_id = serializers.IntegerField()
    operations = BatchOperationSerializer(many=True)
    atomic = serializers.BooleanField(default=True)
    
    def validate_operations(self, operations):
        """Validate batch operations."""
        if len(operations) > 1000:  # Limit batch size
            raise serializers.ValidationError("Maximum 1000 operations per batch")
        
        for operation in operations:
            op_type = operation['operation']
            if op_type in ['update', 'delete'] and not operation.get('row_id'):
                raise serializers.ValidationError(
                    f"{op_type} operations require row_id"
                )
            if op_type == 'create' and not operation.get('data'):
                raise serializers.ValidationError(
                    "Create operations require data"
                )
        
        return operations


class BatchOperationResultSerializer(serializers.Serializer):
    """Serializer for batch operation results."""
    operation_index = serializers.IntegerField()
    operation = serializers.CharField()
    success = serializers.BooleanField()
    row_id = serializers.IntegerField(required=False, allow_null=True)
    data = serializers.JSONField(required=False)
    error = serializers.CharField(required=False, allow_null=True)


class BatchRecordResponseSerializer(serializers.Serializer):
    """Serializer for batch record operation responses."""
    success = serializers.BooleanField()
    total_operations = serializers.IntegerField()
    successful_operations = serializers.IntegerField()
    failed_operations = serializers.IntegerField()
    results = BatchOperationResultSerializer(many=True)
    transaction_id = serializers.CharField(required=False, allow_null=True)