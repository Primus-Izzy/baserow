# Baserow Security and Compliance System

This module implements comprehensive security and compliance features for Baserow, including data encryption, audit logging, GDPR compliance, and rate limiting.

## Features

### 1. Data Encryption
- **At Rest**: Sensitive field data can be encrypted using AES-256 encryption
- **In Transit**: HTTPS enforcement for sensitive endpoints
- **Key Management**: Secure encryption key generation and storage

### 2. Comprehensive Audit Logging
- **Security Events**: Login attempts, permission changes, data access
- **System Events**: User creation, workspace changes, data exports
- **Severity Levels**: Low, Medium, High, Critical
- **Detailed Context**: IP addresses, user agents, timestamps, event details

### 3. GDPR Compliance
- **Data Export**: Complete user data export in JSON format
- **Data Deletion**: Secure user data deletion with audit trail
- **Consent Management**: Track and manage user consent for data processing
- **Right to Rectification**: Support for data correction requests

### 4. Rate Limiting and Monitoring
- **Flexible Rules**: Configurable rate limits per endpoint, user, or IP
- **Multiple Time Windows**: Per-minute, per-hour, and per-day limits
- **Violation Tracking**: Detailed logging of rate limit violations
- **Automatic Blocking**: Temporary blocking of violating IPs/users

## Installation

1. Add the security app to your Django settings:
```python
INSTALLED_APPS = [
    # ... other apps
    'baserow.contrib.security',
]
```

2. Add the security middleware:
```python
MIDDLEWARE = [
    # ... other middleware
    'baserow.contrib.security.middleware.SecurityMiddleware',
    'baserow.contrib.security.middleware.EncryptionMiddleware',
    'baserow.contrib.security.middleware.GDPRComplianceMiddleware',
]
```

3. Configure encryption key:
```bash
python manage.py init_security_system --create-encryption-key
```

4. Create default rate limit rules:
```bash
python manage.py init_security_system --create-rate-limits
```

5. Run migrations:
```bash
python manage.py migrate
```

## Configuration

### Environment Variables

```bash
# Encryption key for data at rest
BASEROW_ENCRYPTION_KEY=your-encryption-key-here

# Paths to skip security checks
SECURITY_SKIP_PATHS=['/health/', '/static/', '/media/']

# Paths that require HTTPS
SECURITY_FORCE_HTTPS_PATHS=['/api/auth/', '/api/user/', '/api/gdpr/']
```

### Rate Limiting

Rate limit rules can be configured through the admin interface or API:

```python
from baserow.contrib.security.models import RateLimitRule

# Create a rate limit rule
RateLimitRule.objects.create(
    name='API Authentication',
    endpoint_pattern=r'/api/auth/.*',
    method='POST',
    requests_per_minute=10,
    requests_per_hour=50,
    requests_per_day=200,
    user_specific=True,
    ip_specific=True
)
```

## API Endpoints

### Security Audit Logs
- `GET /api/security/audit-logs/` - List audit logs
- `GET /api/security/audit-logs/{id}/` - Get specific audit log

### GDPR Requests
- `GET /api/security/gdpr/` - List user's GDPR requests
- `POST /api/security/gdpr/` - Create new GDPR request
- `POST /api/security/gdpr/{id}/process/` - Process GDPR request (admin only)
- `GET /api/security/gdpr/{id}/download/` - Download export file

### Consent Management
- `GET /api/security/consent/` - List user's consent records
- `POST /api/security/consent/grant/` - Grant consent
- `POST /api/security/consent/withdraw/` - Withdraw consent

### Rate Limiting (Admin Only)
- `GET /api/security/rate-limit-rules/` - List rate limit rules
- `POST /api/security/rate-limit-rules/` - Create rate limit rule
- `GET /api/security/rate-limit-violations/` - List violations

### Security Metrics (Admin Only)
- `GET /api/security/metrics/` - Get security metrics

## Usage Examples

### Logging Security Events

```python
from baserow.contrib.security.handler import SecurityHandler

# Log a security event
SecurityHandler.log_security_event(
    event_type='data_access',
    user=request.user,
    ip_address='192.168.1.1',
    user_agent='Mozilla/5.0...',
    details={'table_id': 123, 'action': 'view'},
    severity='low'
)
```

### Encrypting Field Data

```python
from baserow.contrib.security.handler import SecurityHandler

# Encrypt sensitive field data
encrypted_field = SecurityHandler.encrypt_field_value(
    table_id=1,
    field_id=2,
    row_id=3,
    value={'sensitive': 'data'}
)

# Decrypt field data
decrypted_value = SecurityHandler.decrypt_field_value(
    table_id=1,
    field_id=2,
    row_id=3
)
```

### Creating GDPR Requests

```python
from baserow.contrib.security.handler import SecurityHandler

# Create data export request
gdpr_request = SecurityHandler.create_gdpr_request(
    user=user,
    request_type='export',
    details={'format': 'json', 'include_audit_logs': True}
)

# Process the request
export_path = SecurityHandler.process_data_export_request(gdpr_request)
```

### Managing Consent

```python
from baserow.contrib.security.handler import SecurityHandler

# Grant consent
consent = SecurityHandler.grant_consent(
    user=user,
    consent_type='data_processing',
    ip_address='192.168.1.1',
    user_agent='Mozilla/5.0...'
)

# Withdraw consent
SecurityHandler.withdraw_consent(
    user=user,
    consent_type='data_processing'
)
```

## Security Best Practices

1. **Encryption Keys**: Store encryption keys securely, never in version control
2. **Rate Limiting**: Configure appropriate rate limits for your use case
3. **Audit Logs**: Regularly review audit logs for suspicious activity
4. **GDPR Compliance**: Process GDPR requests promptly (within 30 days)
5. **Access Control**: Use proper authentication and authorization
6. **HTTPS**: Always use HTTPS in production
7. **Monitoring**: Set up alerts for critical security events

## Monitoring and Alerting

The security system provides metrics that can be used for monitoring:

```python
from baserow.contrib.security.handler import SecurityHandler

metrics = SecurityHandler.get_security_metrics()
# Returns:
# {
#     'audit_events_24h': 150,
#     'failed_logins_24h': 5,
#     'rate_limit_violations_24h': 2,
#     'gdpr_requests_pending': 1,
#     'critical_events_7d': 0,
#     'high_severity_events_7d': 3
# }
```

Set up alerts for:
- High number of failed login attempts
- Critical security events
- Rate limit violations
- Pending GDPR requests

## Database Schema

The security system creates the following tables:
- `baserow_security_audit_log` - Security event logs
- `baserow_encrypted_fields` - Encrypted field data
- `baserow_gdpr_requests` - GDPR compliance requests
- `baserow_consent_records` - User consent tracking
- `baserow_rate_limit_rules` - Rate limiting configuration
- `baserow_rate_limit_violations` - Rate limit violation logs

## Testing

Run the security system tests:

```bash
python manage.py test baserow.contrib.security
```

The test suite covers:
- Security event logging
- Data encryption/decryption
- GDPR request processing
- Consent management
- Rate limiting
- Middleware functionality