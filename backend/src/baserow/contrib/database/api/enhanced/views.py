"""
Enhanced API views for expanded endpoints.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Max
from django.utils import timezone

from baserow.api.decorators import validate_body, map_exceptions
from baserow.api.errors import ERROR_USER_NOT_IN_GROUP
from baserow.api.pagination import PageNumberPagination
from baserow.core.exceptions import UserNotInGroup
from baserow.core.models import Group, GroupUser
from baserow.contrib.database.models import Database, Table
from baserow.contrib.database.views.models import View

from .serializers import (
    EnhancedUserSerializer,
    EnhancedGroupSerializer,
    EnhancedViewSerializer,
    EnhancedTableSerializer,
    EnhancedDatabaseSerializer,
    APIKeySerializer
)

User = get_user_model()


class EnhancedUserViewSet(ReadOnlyModelViewSet):
    """Enhanced user management API."""
    
    serializer_class = EnhancedUserSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get users accessible to the current user."""
        # Users can see other users in their groups
        user_groups = Group.objects.filter(users=self.request.user)
        return User.objects.filter(
            Q(groups__in=user_groups) | Q(id=self.request.user.id)
        ).distinct().annotate(
            last_active=Max('last_login')
        )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user details."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def groups(self, request, pk=None):
        """Get user's group memberships."""
        user = self.get_object()
        group_users = GroupUser.objects.filter(user=user).select_related('group')
        
        groups_data = []
        for gu in group_users:
            groups_data.append({
                'id': gu.group.id,
                'name': gu.group.name,
                'permissions': gu.permissions,
                'joined_at': gu.created_on,
                'role': 'admin' if gu.permissions == 'ADMIN' else 'member'
            })
        
        return Response(groups_data)


class EnhancedGroupViewSet(ModelViewSet):
    """Enhanced group management API."""
    
    serializer_class = EnhancedGroupSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get groups accessible to the current user."""
        return Group.objects.filter(users=self.request.user).annotate(
            member_count=Count('users')
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get group members with detailed information."""
        group = self.get_object()
        group_users = GroupUser.objects.filter(group=group).select_related('user')
        
        members_data = []
        for gu in group_users:
            members_data.append({
                'id': gu.user.id,
                'email': gu.user.email,
                'first_name': gu.user.first_name,
                'last_name': gu.user.last_name,
                'permissions': gu.permissions,
                'joined_at': gu.created_on,
                'last_active': gu.user.last_login,
                'is_active': gu.user.is_active
            })
        
        return Response(members_data)
    
    @action(detail=True, methods=['get'])
    def activity(self, request, pk=None):
        """Get group activity summary."""
        group = self.get_object()
        
        # Get recent activity (this would integrate with activity logging)
        activity_data = {
            'total_databases': group.database_set.count(),
            'total_tables': Table.objects.filter(database__group=group).count(),
            'total_views': View.objects.filter(table__database__group=group).count(),
            'active_members': group.users.filter(is_active=True).count(),
            'recent_activity': []  # Would be populated from activity logs
        }
        
        return Response(activity_data)


class EnhancedViewViewSet(ReadOnlyModelViewSet):
    """Enhanced view management API."""
    
    serializer_class = EnhancedViewSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get views accessible to the current user."""
        return View.objects.filter(
            table__database__group__users=self.request.user
        ).select_related(
            'table', 'table__database', 'table__database__group'
        ).annotate(
            last_modified=Max('updated_on')
        )
    
    def list(self, request, *args, **kwargs):
        """List views with filtering options."""
        queryset = self.get_queryset()
        
        # Apply filters
        view_type = request.query_params.get('type')
        if view_type:
            queryset = queryset.filter(type=view_type)
        
        table_id = request.query_params.get('table_id')
        if table_id:
            queryset = queryset.filter(table_id=table_id)
        
        database_id = request.query_params.get('database_id')
        if database_id:
            queryset = queryset.filter(table__database_id=database_id)
        
        group_id = request.query_params.get('group_id')
        if group_id:
            queryset = queryset.filter(table__database__group_id=group_id)
        
        # Apply search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Apply ordering
        ordering = request.query_params.get('ordering', '-updated_on')
        queryset = queryset.order_by(ordering)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EnhancedTableViewSet(ReadOnlyModelViewSet):
    """Enhanced table management API."""
    
    serializer_class = EnhancedTableSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get tables accessible to the current user."""
        return Table.objects.filter(
            database__group__users=self.request.user
        ).select_related(
            'database', 'database__group'
        ).annotate(
            last_modified=Max('updated_on')
        )


class EnhancedDatabaseViewSet(ReadOnlyModelViewSet):
    """Enhanced database management API."""
    
    serializer_class = EnhancedDatabaseSerializer
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get databases accessible to the current user."""
        return Database.objects.filter(
            group__users=self.request.user
        ).select_related('group').annotate(
            last_modified=Max('updated_on')
        )


class APIStatsView(APIView):
    """API endpoint for system statistics."""
    
    def get(self, request):
        """Get API usage statistics."""
        user = request.user
        
        # Get user's accessible resources
        user_groups = Group.objects.filter(users=user)
        databases = Database.objects.filter(group__in=user_groups)
        tables = Table.objects.filter(database__in=databases)
        views = View.objects.filter(table__in=tables)
        
        stats = {
            'user': {
                'id': user.id,
                'email': user.email,
                'groups_count': user_groups.count(),
                'last_login': user.last_login
            },
            'resources': {
                'databases': databases.count(),
                'tables': tables.count(),
                'views': views.count(),
                'total_rows': sum(table.get_model().objects.count() for table in tables)
            },
            'api_info': {
                'version': '2.0',
                'endpoints': {
                    'databases': '/api/database/enhanced/databases/',
                    'tables': '/api/database/enhanced/tables/',
                    'views': '/api/database/enhanced/views/',
                    'users': '/api/database/enhanced/users/',
                    'groups': '/api/database/enhanced/groups/',
                    'batch_operations': '/api/database/batch/records/',
                    'webhooks': '/api/database/webhooks/'
                }
            }
        }
        
        return Response(stats)


class APIKeyManagementView(APIView):
    """API endpoint for managing API keys."""
    
    @validate_body(APIKeySerializer)
    def post(self, request, data):
        """Create a new API key."""
        # This would integrate with a proper API key management system
        api_key_data = {
            'name': data['name'],
            'key': f"brow_{timezone.now().strftime('%Y%m%d')}_{user.id}_{uuid.uuid4().hex[:16]}",
            'permissions': data['permissions'],
            'expires_at': data.get('expires_at'),
            'created_at': timezone.now(),
            'user_id': request.user.id
        }
        
        return Response({
            'message': 'API key created successfully',
            'api_key': api_key_data['key'],
            'permissions': api_key_data['permissions'],
            'expires_at': api_key_data['expires_at']
        }, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        """List user's API keys."""
        # This would retrieve from a proper API key storage system
        return Response({
            'api_keys': [
                {
                    'id': 1,
                    'name': 'Development Key',
                    'key_preview': 'brow_20241201_1_abc123...',
                    'permissions': ['database.read', 'table.read', 'row.read'],
                    'created_at': timezone.now(),
                    'last_used': timezone.now(),
                    'expires_at': None
                }
            ]
        })