from rest_framework import serializers
from baserow.contrib.dashboard.models import DashboardExport


class CreateExportSerializer(serializers.Serializer):
    """Serializer for creating dashboard exports."""
    
    export_format = serializers.ChoiceField(choices=DashboardExport.EXPORT_FORMATS)
    configuration = serializers.JSONField(required=False, default=dict)
    delivery_email = serializers.EmailField(required=False)
    schedule_config = serializers.JSONField(required=False)
    
    def validate_schedule_config(self, value):
        if value:
            # Validate schedule configuration structure
            if 'type' not in value:
                raise serializers.ValidationError("Schedule type is required")
            
            if value['type'] not in ['daily', 'weekly', 'monthly']:
                raise serializers.ValidationError("Invalid schedule type")
        
        return value


class ExportStatusSerializer(serializers.ModelSerializer):
    """Serializer for export job status."""
    
    download_url = serializers.SerializerMethodField()
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = DashboardExport
        fields = [
            'id', 'dashboard_name', 'export_format', 'status',
            'created_at', 'completed_at', 'file_size', 'download_url',
            'error_message', 'is_scheduled', 'next_run', 'delivery_email'
        ]
        read_only_fields = [
            'id', 'dashboard_name', 'status', 'created_at', 'completed_at',
            'file_size', 'download_url', 'error_message'
        ]
    
    def get_download_url(self, obj):
        if obj.status == 'completed' and obj.file_path:
            from django.conf import settings
            return f"{settings.PUBLIC_BACKEND_URL}/api/dashboard/exports/{obj.id}/download/"
        return None


class ExportListSerializer(serializers.ModelSerializer):
    """Serializer for listing export jobs."""
    
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = DashboardExport
        fields = [
            'id', 'dashboard_name', 'export_format', 'status',
            'created_at', 'completed_at', 'file_size', 'is_scheduled',
            'next_run'
        ]


class ScheduleExportSerializer(serializers.Serializer):
    """Serializer for scheduling recurring exports."""
    
    export_format = serializers.ChoiceField(choices=DashboardExport.EXPORT_FORMATS)
    schedule_type = serializers.ChoiceField(choices=['daily', 'weekly', 'monthly'])
    delivery_email = serializers.EmailField()
    configuration = serializers.JSONField(required=False, default=dict)
    
    def validate(self, data):
        # Build schedule configuration
        data['schedule_config'] = {
            'type': data.pop('schedule_type'),
            'enabled': True
        }
        return data