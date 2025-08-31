"""
Feature flags system for Baserow expansion features.
Allows gradual rollout and A/B testing of new functionality.
"""

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.contrib.auth import get_user_model
from typing import Dict, Any, Optional
import json
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class FeatureFlag(models.Model):
    """Model for storing feature flag configurations."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    rollout_percentage = models.IntegerField(default=0, help_text="Percentage of users to enable for (0-100)")
    target_groups = models.JSONField(default=list, help_text="List of user groups to target")
    conditions = models.JSONField(default=dict, help_text="Additional conditions for flag evaluation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'baserow_expansion_feature_flags'

    def __str__(self):
        return f"{self.name} ({'enabled' if self.is_enabled else 'disabled'})"


class FeatureFlagManager:
    """Manager class for feature flag operations."""
    
    CACHE_PREFIX = "feature_flag:"
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Default feature flags for expansion features
    DEFAULT_FLAGS = {
        'kanban_view': {
            'description': 'Enable Kanban view functionality',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'timeline_view': {
            'description': 'Enable Timeline/Gantt view functionality',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'calendar_view': {
            'description': 'Enable Calendar view functionality',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'enhanced_table_view': {
            'description': 'Enable enhanced table view features',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'formula_fields': {
            'description': 'Enable formula field type',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'rollup_fields': {
            'description': 'Enable rollup field type',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'people_fields': {
            'description': 'Enable people/owner field type',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'progress_bar_fields': {
            'description': 'Enable progress bar field type',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'automation_system': {
            'description': 'Enable automation and workflow system',
            'is_enabled': False,
            'rollout_percentage': 25
        },
        'visual_automation_builder': {
            'description': 'Enable visual automation builder',
            'is_enabled': False,
            'rollout_percentage': 10
        },
        'real_time_collaboration': {
            'description': 'Enable real-time collaboration features',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'commenting_system': {
            'description': 'Enable commenting and @mentions',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'activity_logging': {
            'description': 'Enable comprehensive activity logging',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'notification_system': {
            'description': 'Enable notification system',
            'is_enabled': False,
            'rollout_percentage': 50
        },
        'dashboard_widgets': {
            'description': 'Enable dashboard and reporting widgets',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'advanced_charts': {
            'description': 'Enable advanced chart types',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'dashboard_sharing': {
            'description': 'Enable dashboard sharing and export',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'granular_permissions': {
            'description': 'Enable granular permission system',
            'is_enabled': False,
            'rollout_percentage': 30
        },
        'security_features': {
            'description': 'Enable advanced security and compliance features',
            'is_enabled': False,
            'rollout_percentage': 20
        },
        'native_integrations': {
            'description': 'Enable native integrations (Google, Slack, etc.)',
            'is_enabled': False,
            'rollout_percentage': 40
        },
        'enhanced_api': {
            'description': 'Enable enhanced API capabilities',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'mobile_optimization': {
            'description': 'Enable mobile-specific optimizations',
            'is_enabled': True,
            'rollout_percentage': 100
        },
        'mobile_features': {
            'description': 'Enable mobile-specific features (offline, push notifications)',
            'is_enabled': False,
            'rollout_percentage': 15
        }
    }
    
    @classmethod
    def is_enabled(cls, flag_name: str, user: Optional[User] = None, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if a feature flag is enabled for a given user and context.
        
        Args:
            flag_name: Name of the feature flag
            user: User to check the flag for (optional)
            context: Additional context for flag evaluation (optional)
            
        Returns:
            bool: True if the flag is enabled, False otherwise
        """
        try:
            # Check cache first
            cache_key = f"{cls.CACHE_PREFIX}{flag_name}"
            if user:
                cache_key += f":user:{user.id}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get flag from database
            try:
                flag = FeatureFlag.objects.get(name=flag_name)
            except FeatureFlag.DoesNotExist:
                # Return False for unknown flags
                logger.warning(f"Feature flag '{flag_name}' not found")
                cache.set(cache_key, False, cls.CACHE_TIMEOUT)
                return False
            
            # Check if flag is globally disabled
            if not flag.is_enabled:
                cache.set(cache_key, False, cls.CACHE_TIMEOUT)
                return False
            
            # Check rollout percentage
            if flag.rollout_percentage < 100 and user:
                user_hash = hash(f"{flag_name}:{user.id}") % 100
                if user_hash >= flag.rollout_percentage:
                    cache.set(cache_key, False, cls.CACHE_TIMEOUT)
                    return False
            
            # Check target groups
            if flag.target_groups and user:
                user_groups = set(user.groups.values_list('name', flat=True))
                if not any(group in user_groups for group in flag.target_groups):
                    cache.set(cache_key, False, cls.CACHE_TIMEOUT)
                    return False
            
            # Check additional conditions
            if flag.conditions and not cls._evaluate_conditions(flag.conditions, user, context):
                cache.set(cache_key, False, cls.CACHE_TIMEOUT)
                return False
            
            # Flag is enabled
            cache.set(cache_key, True, cls.CACHE_TIMEOUT)
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating feature flag '{flag_name}': {e}")
            return False
    
    @classmethod
    def _evaluate_conditions(cls, conditions: Dict[str, Any], user: Optional[User], context: Optional[Dict[str, Any]]) -> bool:
        """Evaluate additional conditions for feature flag."""
        try:
            # Example condition evaluations
            if 'min_user_id' in conditions and user:
                if user.id < conditions['min_user_id']:
                    return False
            
            if 'workspace_id' in conditions and context:
                if context.get('workspace_id') != conditions['workspace_id']:
                    return False
            
            if 'user_email_domain' in conditions and user:
                required_domain = conditions['user_email_domain']
                if not user.email.endswith(f"@{required_domain}"):
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error evaluating feature flag conditions: {e}")
            return False
    
    @classmethod
    def get_enabled_flags(cls, user: Optional[User] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """Get all enabled flags for a user."""
        flags = {}
        for flag in FeatureFlag.objects.all():
            flags[flag.name] = cls.is_enabled(flag.name, user, context)
        return flags
    
    @classmethod
    def clear_cache(cls, flag_name: Optional[str] = None, user: Optional[User] = None):
        """Clear feature flag cache."""
        if flag_name and user:
            cache_key = f"{cls.CACHE_PREFIX}{flag_name}:user:{user.id}"
            cache.delete(cache_key)
        elif flag_name:
            # Clear all user-specific caches for this flag
            cache.delete_many([f"{cls.CACHE_PREFIX}{flag_name}"])
        else:
            # Clear all feature flag caches
            cache.clear()
    
    @classmethod
    def initialize_default_flags(cls):
        """Initialize default feature flags."""
        for flag_name, config in cls.DEFAULT_FLAGS.items():
            flag, created = FeatureFlag.objects.get_or_create(
                name=flag_name,
                defaults=config
            )
            if created:
                logger.info(f"Created default feature flag: {flag_name}")


# Convenience function for templates and views
def is_feature_enabled(flag_name: str, user: Optional[User] = None, context: Optional[Dict[str, Any]] = None) -> bool:
    """Convenience function to check if a feature flag is enabled."""
    return FeatureFlagManager.is_enabled(flag_name, user, context)