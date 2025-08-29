from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.db.models import Q
import os

from baserow.api.decorators import validate_body, map_exceptions
from baserow.api.pagination import PageNumberPagination
from baserow.core.exceptions import UserNotInWorkspace

from ..models import SecurityAuditLog, GDPRRequest, ConsentRecord, RateLimitRule, RateLimitViolation
from ..handler import SecurityHandler
from .serializers import (
    SecurityAuditLogSerializer, GDPRRequestSerializer, GDPRRequestCreateSerializer,
    ConsentRecordSerializer, ConsentGrantSerializer, ConsentWithdrawSerializer,
    RateLimitRuleSerializer, RateLimitViolationSerializer, SecurityMetricsSerializer,
    DataExportSerializer
)

User = get_user_model()


class SecurityAuditLogViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for viewing security audit logs.
    """
    serializer_class = SecurityAuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        queryset = SecurityAuditLog.objects.all().order_by('-timestamp')
        
        # Filter by user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Apply filters
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset


class GDPRRequestViewSet(ModelViewSet):
    """
    ViewSet for managing GDPR requests.
    """
    serializer_class = GDPRRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        # Users can only see their own GDPR requests
        return GDPRRequest.objects.filter(user=self.request.user).order_by('-requested_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GDPRRequestCreateSerializer
        return GDPRRequestSerializer
    
    @validate_body(GDPRRequestCreateSerializer)
    def create(self, request, data):
        """
        Create a new GDPR request.
        """
        gdpr_request = SecurityHandler.create_gdpr_request(
            user=request.user,
            request_type=data['request_type'],
            details=data.get('details', {})
        )
        
        serializer = GDPRRequestSerializer(gdpr_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Process a GDPR request (admin only).
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        gdpr_request = self.get_object()
        
        if gdpr_request.request_type == 'export':
            try:
                export_path = SecurityHandler.process_data_export_request(gdpr_request)
                return Response({
                    'message': 'Export completed',
                    'export_file': os.path.basename(export_path)
                })
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif gdpr_request.request_type == 'deletion':
            try:
                SecurityHandler.process_data_deletion_request(gdpr_request)
                return Response({'message': 'Deletion completed'})
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            {'error': 'Unsupported request type'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download exported data file.
        """
        gdpr_request = self.get_object()
        
        if gdpr_request.request_type != 'export' or gdpr_request.status != 'completed':
            raise Http404("Export file not available")
        
        if not gdpr_request.export_file_path or not os.path.exists(gdpr_request.export_file_path):
            raise Http404("Export file not found")
        
        with open(gdpr_request.export_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(gdpr_request.export_file_path)}"'
            return response


class ConsentRecordViewSet(ModelViewSet):
    """
    ViewSet for managing consent records.
    """
    serializer_class = ConsentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ConsentRecord.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    @validate_body(ConsentGrantSerializer)
    def grant(self, request, data):
        """
        Grant consent for data processing.
        """
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        consent = SecurityHandler.grant_consent(
            user=request.user,
            consent_type=data['consent_type'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        serializer = ConsentRecordSerializer(consent)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    @validate_body(ConsentWithdrawSerializer)
    def withdraw(self, request, data):
        """
        Withdraw consent for data processing.
        """
        consent = SecurityHandler.withdraw_consent(
            user=request.user,
            consent_type=data['consent_type']
        )
        
        if consent:
            serializer = ConsentRecordSerializer(consent)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Consent record not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitRuleViewSet(ModelViewSet):
    """
    ViewSet for managing rate limit rules (admin only).
    """
    serializer_class = RateLimitRuleSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        return RateLimitRule.objects.all().order_by('-created_at')


class RateLimitViolationViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for viewing rate limit violations (admin only).
    """
    serializer_class = RateLimitViolationSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        return RateLimitViolation.objects.all().order_by('-timestamp')


class SecurityMetricsView(APIView):
    """
    API view for security metrics.
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """
        Get security metrics for monitoring dashboard.
        """
        metrics = SecurityHandler.get_security_metrics()
        serializer = SecurityMetricsSerializer(metrics)
        return Response(serializer.data)


class DataExportView(APIView):
    """
    API view for exporting user data.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @validate_body(DataExportSerializer)
    def post(self, request, data):
        """
        Create a data export request.
        """
        gdpr_request = SecurityHandler.create_gdpr_request(
            user=request.user,
            request_type='export',
            details=data
        )
        
        # Process the export immediately for now
        # In production, this should be handled by a background task
        try:
            export_path = SecurityHandler.process_data_export_request(gdpr_request)
            
            # Return download link
            return Response({
                'message': 'Export completed',
                'download_url': f'/api/security/gdpr/{gdpr_request.id}/download/',
                'request_id': gdpr_request.id
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )