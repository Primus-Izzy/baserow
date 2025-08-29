from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SecurityAuditLogViewSet, GDPRRequestViewSet, ConsentRecordViewSet,
    RateLimitRuleViewSet, RateLimitViolationViewSet, SecurityMetricsView,
    DataExportView
)

app_name = "baserow.contrib.security.api"

router = DefaultRouter()
router.register("audit-logs", SecurityAuditLogViewSet, basename="audit_logs")
router.register("gdpr", GDPRRequestViewSet, basename="gdpr_requests")
router.register("consent", ConsentRecordViewSet, basename="consent_records")
router.register("rate-limit-rules", RateLimitRuleViewSet, basename="rate_limit_rules")
router.register("rate-limit-violations", RateLimitViolationViewSet, basename="rate_limit_violations")

urlpatterns = [
    path("metrics/", SecurityMetricsView.as_view(), name="security_metrics"),
    path("export/", DataExportView.as_view(), name="data_export"),
    path("", include(router.urls)),
]