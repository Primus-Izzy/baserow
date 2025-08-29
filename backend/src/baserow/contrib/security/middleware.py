import logging
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import json

from .handler import SecurityHandler

User = get_user_model()
logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware for security monitoring, rate limiting, and audit logging.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """
        Process incoming requests for security checks.
        """
        # Skip security checks for certain paths
        skip_paths = getattr(settings, 'SECURITY_SKIP_PATHS', [
            '/health/',
            '/static/',
            '/media/',
        ])
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None

        # Get client information
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

        # Store security context for later use
        request.security_context = {
            'ip_address': ip_address,
            'user_agent': user_agent,
            'user': user,
            'timestamp': timezone.now(),
            'endpoint': request.path,
            'method': request.method,
        }

        # Check rate limits
        if not SecurityHandler.check_rate_limit(
            endpoint=request.path,
            method=request.method,
            user=user,
            ip_address=ip_address
        ):
            # Log rate limit violation
            SecurityHandler.log_security_event(
                event_type='rate_limit_exceeded',
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'endpoint': request.path,
                    'method': request.method,
                },
                severity='medium',
                success=False
            )
            
            return HttpResponse(
                json.dumps({'error': 'Rate limit exceeded'}),
                status=429,
                content_type='application/json'
            )

        return None

    def process_response(self, request, response):
        """
        Process responses for security logging.
        """
        # Skip if no security context
        if not hasattr(request, 'security_context'):
            return response

        context = request.security_context
        
        # Log API access for monitoring
        if request.path.startswith('/api/'):
            SecurityHandler.log_security_event(
                event_type='api_access',
                user=context['user'],
                ip_address=context['ip_address'],
                user_agent=context['user_agent'],
                details={
                    'endpoint': context['endpoint'],
                    'method': context['method'],
                    'status_code': response.status_code,
                },
                severity='low',
                success=response.status_code < 400
            )

        # Log failed authentication attempts
        if response.status_code == 401:
            SecurityHandler.log_security_event(
                event_type='failed_login',
                user=context['user'],
                ip_address=context['ip_address'],
                user_agent=context['user_agent'],
                details={
                    'endpoint': context['endpoint'],
                    'method': context['method'],
                },
                severity='medium',
                success=False
            )

        # Log permission denied events
        if response.status_code == 403:
            SecurityHandler.log_security_event(
                event_type='permission_denied',
                user=context['user'],
                ip_address=context['ip_address'],
                user_agent=context['user_agent'],
                details={
                    'endpoint': context['endpoint'],
                    'method': context['method'],
                },
                severity='medium',
                success=False
            )

        return response

    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EncryptionMiddleware(MiddlewareMixin):
    """
    Middleware for handling data encryption in transit.
    """

    def process_request(self, request):
        """
        Ensure HTTPS for sensitive endpoints.
        """
        # Force HTTPS for sensitive endpoints
        sensitive_paths = getattr(settings, 'SECURITY_FORCE_HTTPS_PATHS', [
            '/api/auth/',
            '/api/user/',
            '/api/gdpr/',
        ])
        
        if any(request.path.startswith(path) for path in sensitive_paths):
            if not request.is_secure() and not settings.DEBUG:
                # Log security violation
                SecurityHandler.log_security_event(
                    event_type='insecure_request',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details={
                        'endpoint': request.path,
                        'method': request.method,
                    },
                    severity='high',
                    success=False
                )
                
                return HttpResponse(
                    json.dumps({'error': 'HTTPS required for this endpoint'}),
                    status=400,
                    content_type='application/json'
                )

        return None

    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GDPRComplianceMiddleware(MiddlewareMixin):
    """
    Middleware for GDPR compliance tracking.
    """

    def process_request(self, request):
        """
        Track data processing activities for GDPR compliance.
        """
        # Track data access for authenticated users
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            request.path.startswith('/api/database/')):
            
            # Log data access
            SecurityHandler.log_security_event(
                event_type='data_access',
                user=request.user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'endpoint': request.path,
                    'method': request.method,
                },
                severity='low'
            )

        return None

    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip