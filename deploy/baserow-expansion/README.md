# Baserow Expansion Deployment Guide

This directory contains deployment configurations and scripts for the Baserow expansion features.

## Quick Start

1. **Configure Environment**
   ```bash
   cp .env.production .env.local
   # Edit .env.local with your specific configuration
   ```

2. **Deploy**
   ```bash
   ./deploy.sh production
   ```

3. **Verify Deployment**
   - Check health: `curl http://localhost:8000/api/health/`
   - View metrics: `http://localhost:9090` (Prometheus)
   - Access dashboards: `http://localhost:3000` (Grafana)

## Files Overview

### Docker Configuration
- `docker-compose.expansion.yml` - Main Docker Compose configuration
- `Dockerfile.expansion` - Custom Dockerfile with expansion features
- `.env.production` - Production environment template

### Scripts
- `deploy.sh` - Main deployment script with rollback capability
- `health-check.sh` - Container health check script
- `scripts/start-expansion.sh` - Container startup script
- `scripts/backup.sh` - Comprehensive backup script
- `scripts/restore.sh` - Backup restoration script
- `scripts/post-deploy-tests.sh` - Post-deployment verification tests

### Monitoring
- `monitoring/prometheus.yml` - Prometheus configuration
- `monitoring/alert_rules.yml` - Alerting rules
- `monitoring/alertmanager.yml` - Alert manager configuration

## Environment Configuration

### Required Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# Application
SECRET_KEY=your-secret-key
BASEROW_PUBLIC_URL=https://your-domain.com

# Monitoring
MONITORING_ENABLED=true
SENTRY_DSN=your-sentry-dsn
```

### Feature Flags
Control feature rollout with environment variables:
```bash
FEATURE_FLAGS=kanban_view:true,timeline_view:true,automation_system:false
```

## Deployment Process

### 1. Pre-deployment
- Backup current data
- Build new Docker images
- Run database migrations

### 2. Deployment
- Start new services
- Health checks
- Post-deployment tests

### 3. Post-deployment
- Verify all services
- Monitor metrics
- Send notifications

## Monitoring

### Prometheus Metrics
- Application performance metrics
- Database connection counts
- Cache hit rates
- Celery queue lengths

### Health Checks
- Database connectivity
- Redis connectivity
- Celery workers
- Application responsiveness

### Alerting
- Service downtime
- High error rates
- Performance degradation
- Resource exhaustion

## Backup and Recovery

### Automated Backups
```bash
# Run backup manually
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh backup_name
```

### Backup Components
- PostgreSQL database (custom and SQL formats)
- Redis data
- File storage
- Configuration and feature flags

## Troubleshooting

### Common Issues

1. **Health Check Failures**
   ```bash
   # Check logs
   docker-compose logs baserow-expansion
   
   # Verify database connection
   docker-compose exec postgres pg_isready
   ```

2. **Migration Errors**
   ```bash
   # Run migrations manually
   docker-compose run --rm baserow-expansion python manage.py migrate
   ```

3. **Feature Flag Issues**
   ```bash
   # Reset feature flags
   docker-compose run --rm baserow-expansion python manage.py initialize_feature_flags --reset
   ```

### Log Locations
- Application logs: `docker-compose logs baserow-expansion`
- Database logs: `docker-compose logs postgres`
- Monitoring logs: `docker-compose logs prometheus grafana`

## Security Considerations

### Production Checklist
- [ ] Change default passwords
- [ ] Configure SSL/TLS
- [ ] Set up firewall rules
- [ ] Enable audit logging
- [ ] Configure backup encryption
- [ ] Set up monitoring alerts
- [ ] Review feature flag settings

### Environment Security
- Use strong, unique passwords
- Enable SSL for all external connections
- Configure proper network isolation
- Regular security updates
- Monitor access logs

## Performance Tuning

### Database Optimization
- Connection pooling
- Query optimization
- Index management
- Regular maintenance

### Application Scaling
- Horizontal scaling with load balancers
- Celery worker scaling
- Redis clustering
- CDN for static files

## Support

For deployment issues:
1. Check the troubleshooting section
2. Review application logs
3. Verify configuration
4. Check monitoring dashboards
5. Contact support with specific error messages