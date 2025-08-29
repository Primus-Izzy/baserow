from rest_framework import serializers
from django.contrib.auth import get_user_model

from ..models import SecurityAuditLog, GDPRRequest, ConsentRecord, RateLimitRule, RateLimitViolation

User = get_user_model()


class SecurityAuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for security audit logs.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = SecurityAuditLog
        fields = [
            'id', 'user', 'user_email', 'event_type', 'severity',
            'ip_address', 'user_agent', 'timestamp', 'details', 'success'
        ]
        read_only_fields = ['id', 'timestamp']


class GDPRRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for GDPR requests.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = GDPRRequest
        fields = [
            'id', 'user', 'user_email', 'request_type', 'status',
            'requested_at', 'processed_at', 'completed_at', 'details'
        ]
        read_only_fields = ['id', 'user', 'requested_at', 'processed_at', 'completed_at']


class GDPRRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating GDPR requests.
    """
    class Meta:
        model = GDPRRequest
        fields = ['request_type', 'details']


class ConsentRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for consent records.
    """
    class Meta:
        model = ConsentRecord
        fields = [
            'id', 'consent_type', 'granted', 'granted_at', 'withdrawn_at'
        ]
        read_only_fields = ['id', 'granted_at', 'withdrawn_at']


class ConsentGrantSerializer(serializers.Serializer):
    """
    Serializer for granting consent.
    """
    consent_type = serializers.ChoiceField(choices=ConsentRecord.CONSENT_TYPES)


class ConsentWithdrawSerializer(serializers.Serializer):
    """
    Serializer for withdrawing consent.
    """
    consent_type = serializers.ChoiceField(choices=ConsentRecord.CONSENT_TYPES)


class RateLimitRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for rate limit rules.
    """
    class Meta:
        model = RateLimitRule
        fields = [
            'id', 'name', 'endpoint_pattern', 'method',
            'requests_per_minute', 'requests_per_hour', 'requests_per_day',
            'user_specific', 'ip_specific', 'burst_allowance', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RateLimitViolationSerializer(serializers.ModelSerializer):
    """
    Serializer for rate limit violations.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    
    class Meta:
        model = RateLimitViolation
        fields = [
            'id', 'rule', 'rule_name', 'user', 'user_email',
            'ip_address', 'endpoint', 'method', 'timestamp', 'requests_count'
        ]
        read_only_fields = ['id', 'timestamp']


class SecurityMetricsSerializer(serializers.Serializer):
    """
    Serializer for security metrics.
    """
    audit_events_24h = serializers.IntegerField()
    failed_logins_24h = serializers.IntegerField()
    rate_limit_violations_24h = serializers.IntegerField()
    gdpr_requests_pending = serializers.IntegerField()
    critical_events_7d = serializers.IntegerField()
    high_severity_events_7d = serializers.IntegerField()


class DataExportSerializer(serializers.Serializer):
    """
    Serializer for data export requests.
    """
    export_format = serializers.ChoiceField(
        choices=[('json', 'JSON'), ('csv', 'CSV')],
        default='json'
    )
    include_audit_logs = serializers.BooleanField(default=True)
    include_consent_records = serializers.BooleanField(default=True)