# Architecture Overview

This document provides a comprehensive overview of Baserow's architecture after the Monday.com-style expansion, covering both the technical implementation and design decisions.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Vue.js/Nuxt.js SPA  │  Mobile PWA  │  Embedded Widgets    │
│  - Real-time UI      │  - Offline   │  - Public Dashboards │
│  - WebSocket client  │  - Touch UI  │  - Form Embeds       │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Load Balancer   │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Backend Layer                             │
├─────────────────────────────────────────────────────────────┤
│           Django REST API Server                            │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Views     │   Fields    │ Automation  │ Dashboards  │  │
│  │   - Table   │   - Text    │ - Triggers  │ - Widgets   │  │
│  │   - Kanban  │   - Number  │ - Actions   │ - Charts    │  │
│  │   - Timeline│   - People  │ - Workflows │ - KPIs      │  │
│  │   - Calendar│   - Progress│ - Scheduler │ - Exports   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
│                              │                              │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │Collaboration│ Permissions │ Integration │   Caching   │  │
│  │ - Comments  │ - RBAC      │ - Webhooks  │ - Redis     │  │
│  │ - Activity  │ - Field ACL │ - OAuth     │ - Memcached │  │
│  │ - Presence  │ - Row ACL   │ - API Keys  │ - CDN       │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ PostgreSQL  │    Redis    │   S3/Minio  │ Elasticsearch│  │
│  │ - Tables    │ - Sessions  │ - Files     │ - Search     │  │
│  │ - Views     │ - Cache     │ - Exports   │ - Analytics  │  │
│  │ - Users     │ - Queues    │ - Backups   │ - Logs       │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend
- **Framework**: Vue.js 3 with Composition API
- **Meta-Framework**: Nuxt.js 3 for SSR/SPA
- **State Management**: Pinia (Vuex successor)
- **UI Components**: Custom component library + Headless UI
- **Real-time**: WebSocket client with reconnection logic
- **Build Tool**: Vite for fast development and building
- **Testing**: Vitest + Vue Test Utils + Playwright

#### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 14+ with JSON fields
- **Cache**: Redis 6+ for sessions, queues, and caching
- **Search**: Elasticsearch 8+ for full-text search
- **File Storage**: S3-compatible storage (AWS S3, MinIO)
- **Task Queue**: Celery with Redis broker
- **WebSocket**: Django Channels with Redis channel layer

#### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes or Docker Compose
- **Load Balancer**: Nginx or cloud load balancer
- **Monitoring**: Prometheus + Grafana + Sentry
- **CI/CD**: GitHub Actions or GitLab CI

## 🎨 Frontend Architecture

### Component Structure

```
src/
├── components/
│   ├── database/
│   │   ├── views/
│   │   │   ├── BaseView.vue
│   │   │   ├── TableView/
│   │   │   │   ├── TableView.vue
│   │   │   │   ├── TableHeader.vue
│   │   │   │   ├── TableRow.vue
│   │   │   │   └── TableCell.vue
│   │   │   ├── KanbanView/
│   │   │   │   ├── KanbanView.vue
│   │   │   │   ├── KanbanColumn.vue
│   │   │   │   ├── KanbanCard.vue
│   │   │   │   └── KanbanDragDrop.js
│   │   │   ├── TimelineView/
│   │   │   │   ├── TimelineView.vue
│   │   │   │   ├── TimelineGantt.vue
│   │   │   │   ├── TimelineTask.vue
│   │   │   │   └── TimelineDependencies.vue
│   │   │   └── CalendarView/
│   │   │       ├── CalendarView.vue
│   │   │       ├── CalendarMonth.vue
│   │   │       ├── CalendarWeek.vue
│   │   │       └── CalendarEvent.vue
│   │   └── fields/
│   │       ├── BaseField.vue
│   │       ├── TextField.vue
│   │       ├── NumberField.vue
│   │       ├── PeopleField.vue
│   │       ├── ProgressBarField.vue
│   │       └── FormulaField.vue
│   ├── dashboard/
│   │   ├── Dashboard.vue
│   │   ├── DashboardGrid.vue
│   │   └── widgets/
│   │       ├── BaseWidget.vue
│   │       ├── ChartWidget.vue
│   │       ├── KPIWidget.vue
│   │       └── TableWidget.vue
│   ├── automation/
│   │   ├── WorkflowBuilder.vue
│   │   ├── TriggerNode.vue
│   │   ├── ActionNode.vue
│   │   └── FlowCanvas.vue
│   └── collaboration/
│       ├── Comments.vue
│       ├── ActivityFeed.vue
│       ├── UserPresence.vue
│       └── Notifications.vue
├── stores/
│   ├── database.js
│   ├── views.js
│   ├── fields.js
│   ├── collaboration.js
│   ├── automation.js
│   └── dashboard.js
├── composables/
│   ├── useWebSocket.js
│   ├── useRealTime.js
│   ├── usePermissions.js
│   └── useOptimisticUpdates.js
└── plugins/
    ├── api.js
    ├── websocket.js
    └── permissions.js
```

### State Management Pattern

```javascript
// stores/database.js - Pinia store example
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDatabaseStore = defineStore('database', () => {
  // State
  const tables = ref([])
  const currentTable = ref(null)
  const rows = ref([])
  const loading = ref(false)
  
  // Getters
  const currentTableRows = computed(() => {
    return rows.value.filter(row => row.table_id === currentTable.value?.id)
  })
  
  // Actions
  async function fetchTable(tableId) {
    loading.value = true
    try {
      const response = await $api.get(`/database/tables/${tableId}/`)
      currentTable.value = response.data
      await fetchRows(tableId)
    } finally {
      loading.value = false
    }
  }
  
  async function createRow(tableId, data) {
    // Optimistic update
    const tempRow = { id: `temp-${Date.now()}`, ...data, table_id: tableId }
    rows.value.push(tempRow)
    
    try {
      const response = await $api.post(`/database/tables/${tableId}/rows/`, data)
      // Replace temp row with real row
      const index = rows.value.findIndex(r => r.id === tempRow.id)
      rows.value[index] = response.data
    } catch (error) {
      // Remove temp row on error
      rows.value = rows.value.filter(r => r.id !== tempRow.id)
      throw error
    }
  }
  
  return {
    tables,
    currentTable,
    rows,
    loading,
    currentTableRows,
    fetchTable,
    createRow
  }
})
```

### Real-time Updates

```javascript
// composables/useRealTime.js
import { ref, onMounted, onUnmounted } from 'vue'
import { useWebSocket } from './useWebSocket'

export function useRealTime(tableId) {
  const { socket, connect, disconnect } = useWebSocket()
  const isConnected = ref(false)
  
  onMounted(() => {
    connect(`/ws/table/${tableId}/`)
    
    socket.onopen = () => {
      isConnected.value = true
      // Subscribe to table events
      socket.send(JSON.stringify({
        type: 'subscribe',
        events: ['row_created', 'row_updated', 'row_deleted']
      }))
    }
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleRealTimeUpdate(data)
    }
    
    socket.onclose = () => {
      isConnected.value = false
    }
  })
  
  onUnmounted(() => {
    disconnect()
  })
  
  function handleRealTimeUpdate(data) {
    const store = useDatabaseStore()
    
    switch (data.type) {
      case 'row_created':
        store.rows.push(data.row)
        break
      case 'row_updated':
        const index = store.rows.findIndex(r => r.id === data.row.id)
        if (index !== -1) {
          store.rows[index] = { ...store.rows[index], ...data.row }
        }
        break
      case 'row_deleted':
        store.rows = store.rows.filter(r => r.id !== data.row_id)
        break
    }
  }
  
  return { isConnected }
}
```

## 🔧 Backend Architecture

### Django Project Structure

```
backend/
├── src/
│   └── baserow/
│       ├── core/
│       │   ├── models.py
│       │   ├── permissions.py
│       │   ├── exceptions.py
│       │   └── utils.py
│       ├── contrib/
│       │   ├── database/
│       │   │   ├── views/
│       │   │   │   ├── models.py
│       │   │   │   ├── serializers.py
│       │   │   │   ├── viewsets.py
│       │   │   │   └── handlers/
│       │   │   │       ├── table.py
│       │   │   │       ├── kanban.py
│       │   │   │       ├── timeline.py
│       │   │   │       └── calendar.py
│       │   │   ├── fields/
│       │   │   │   ├── models.py
│       │   │   │   ├── serializers.py
│       │   │   │   └── field_types/
│       │   │   │       ├── text_field.py
│       │   │   │       ├── people_field.py
│       │   │   │       ├── progress_field.py
│       │   │   │       └── formula_field.py
│       │   │   └── api/
│       │   │       ├── views.py
│       │   │       ├── serializers.py
│       │   │       └── urls.py
│       │   ├── dashboard/
│       │   │   ├── models.py
│       │   │   ├── widgets/
│       │   │   ├── charts/
│       │   │   └── api/
│       │   ├── automation/
│       │   │   ├── models.py
│       │   │   ├── triggers/
│       │   │   ├── actions/
│       │   │   ├── engine.py
│       │   │   └── api/
│       │   └── collaboration/
│       │       ├── models.py
│       │       ├── comments/
│       │       ├── activity/
│       │       ├── presence/
│       │       └── api/
│       ├── ws/
│       │   ├── consumers.py
│       │   ├── routing.py
│       │   └── middleware.py
│       └── settings/
│           ├── base.py
│           ├── development.py
│           ├── production.py
│           └── testing.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

### Model Architecture

```python
# Core models with inheritance hierarchy
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Extended user model with additional fields"""
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
class Workspace(models.Model):
    """Top-level container for databases and users"""
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, through='WorkspaceUser')
    created_on = models.DateTimeField(auto_now_add=True)
    
class Database(models.Model):
    """Container for related tables"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    
class Table(models.Model):
    """Data table with dynamic schema"""
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    
class Field(models.Model):
    """Base field model with polymorphic field types"""
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True

class View(models.Model):
    """Base view model for different view types"""
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    filters = models.JSONField(default=list)
    sortings = models.JSONField(default=list)
    
    class Meta:
        abstract = True
```

### View Handler Pattern

```python
# views/handlers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseViewHandler(ABC):
    """Base class for all view type handlers"""
    
    type = None  # Override in subclasses
    
    def __init__(self, view_model):
        self.view_model = view_model
    
    @abstractmethod
    def get_serializer_class(self):
        """Return the serializer class for this view type"""
        pass
    
    @abstractmethod
    def prepare_values(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare values before saving"""
        pass
    
    @abstractmethod
    def get_queryset(self, table, **kwargs):
        """Get filtered and sorted queryset for this view"""
        pass
    
    def apply_filters(self, queryset, filters: List[Dict]):
        """Apply view-specific filters"""
        for filter_config in filters:
            queryset = self._apply_single_filter(queryset, filter_config)
        return queryset
    
    def apply_sorting(self, queryset, sortings: List[Dict]):
        """Apply view-specific sorting"""
        order_by = []
        for sort_config in sortings:
            field_name = sort_config['field']
            direction = '-' if sort_config['order'] == 'DESC' else ''
            order_by.append(f"{direction}{field_name}")
        
        if order_by:
            queryset = queryset.order_by(*order_by)
        
        return queryset

# views/handlers/kanban.py
class KanbanViewHandler(BaseViewHandler):
    """Handler for Kanban view type"""
    
    type = 'kanban'
    
    def get_serializer_class(self):
        from ..serializers import KanbanViewSerializer
        return KanbanViewSerializer
    
    def prepare_values(self, values):
        # Validate kanban-specific configuration
        if 'single_select_field' not in values:
            raise ValidationError("Kanban view requires a single select field")
        
        return values
    
    def get_queryset(self, table, **kwargs):
        """Get rows grouped by single select field"""
        queryset = table.get_model().objects.all()
        
        # Apply base filters and sorting
        if self.view_model.filters:
            queryset = self.apply_filters(queryset, self.view_model.filters)
        
        if self.view_model.sortings:
            queryset = self.apply_sorting(queryset, self.view_model.sortings)
        
        return queryset
    
    def get_grouped_rows(self, table):
        """Get rows grouped by kanban columns"""
        queryset = self.get_queryset(table)
        field_name = self.view_model.single_select_field.db_column
        
        # Group by single select field value
        groups = {}
        for row in queryset:
            field_value = getattr(row, field_name, None)
            if field_value not in groups:
                groups[field_value] = []
            groups[field_value].append(row)
        
        return groups
```

### Permission System

```python
# core/permissions.py
from enum import Enum
from typing import List, Dict, Any
from django.contrib.auth.models import Permission

class PermissionLevel(Enum):
    """Permission levels in hierarchical order"""
    WORKSPACE = 'workspace'
    DATABASE = 'database'
    TABLE = 'table'
    VIEW = 'view'
    FIELD = 'field'
    ROW = 'row'

class BaserowPermissionHandler:
    """Centralized permission handling"""
    
    def __init__(self, user):
        self.user = user
        self._permission_cache = {}
    
    def check_permission(self, action: str, obj: Any, **context) -> bool:
        """Check if user has permission for action on object"""
        cache_key = f"{action}:{obj.__class__.__name__}:{obj.id}"
        
        if cache_key in self._permission_cache:
            return self._permission_cache[cache_key]
        
        result = self._check_permission_internal(action, obj, **context)
        self._permission_cache[cache_key] = result
        return result
    
    def _check_permission_internal(self, action: str, obj: Any, **context) -> bool:
        """Internal permission checking logic"""
        # Check workspace-level permissions first
        workspace = self._get_workspace(obj)
        if not self._has_workspace_permission(workspace, action):
            return False
        
        # Check object-specific permissions
        if hasattr(obj, 'check_user_permission'):
            return obj.check_user_permission(self.user, action, **context)
        
        # Default to checking Django permissions
        perm_name = f"{obj._meta.app_label}.{action}_{obj._meta.model_name}"
        return self.user.has_perm(perm_name)
    
    def filter_queryset(self, queryset, action: str = 'view'):
        """Filter queryset based on user permissions"""
        model_class = queryset.model
        
        if hasattr(model_class, 'filter_by_user_permission'):
            return model_class.filter_by_user_permission(queryset, self.user, action)
        
        return queryset  # Default: no filtering

# Field-level permission example
class FieldPermissionMixin:
    """Mixin for field-level permissions"""
    
    def check_user_permission(self, user, action, **context):
        """Check if user can perform action on this field"""
        # Check if field is restricted
        if hasattr(self, 'restricted_to_roles'):
            user_roles = self.table.get_user_roles(user)
            if not any(role in self.restricted_to_roles for role in user_roles):
                return False
        
        # Check conditional permissions
        if hasattr(self, 'permission_conditions'):
            row = context.get('row')
            if row and not self._evaluate_conditions(row, user):
                return False
        
        return True
    
    def _evaluate_conditions(self, row, user):
        """Evaluate conditional permission rules"""
        for condition in self.permission_conditions:
            if not self._evaluate_single_condition(condition, row, user):
                return False
        return True
```

### WebSocket Architecture

```python
# ws/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .permissions import check_websocket_permission

class TableConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time table updates"""
    
    async def connect(self):
        self.table_id = self.scope['url_route']['kwargs']['table_id']
        self.table_group_name = f'table_{self.table_id}'
        self.user = self.scope['user']
        
        # Check permissions
        if not await self.check_table_permission():
            await self.close()
            return
        
        # Join table group
        await self.channel_layer.group_add(
            self.table_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial presence info
        await self.send_presence_update('joined')
    
    async def disconnect(self, close_code):
        # Leave table group
        await self.channel_layer.group_discard(
            self.table_group_name,
            self.channel_name
        )
        
        # Send presence update
        await self.send_presence_update('left')
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                await self.handle_subscribe(data)
            elif message_type == 'cursor_position':
                await self.handle_cursor_position(data)
            elif message_type == 'typing_indicator':
                await self.handle_typing_indicator(data)
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
    
    async def handle_subscribe(self, data):
        """Handle event subscription"""
        events = data.get('events', [])
        # Store subscribed events for this connection
        self.subscribed_events = events
        
        await self.send(text_data=json.dumps({
            'type': 'subscription_confirmed',
            'events': events
        }))
    
    async def handle_cursor_position(self, data):
        """Handle cursor position updates"""
        await self.channel_layer.group_send(
            self.table_group_name,
            {
                'type': 'cursor_position_update',
                'user_id': self.user.id,
                'position': data.get('position'),
                'sender_channel': self.channel_name
            }
        )
    
    async def cursor_position_update(self, event):
        """Send cursor position update to client"""
        # Don't send to the sender
        if event['sender_channel'] == self.channel_name:
            return
            
        await self.send(text_data=json.dumps({
            'type': 'cursor_position',
            'user_id': event['user_id'],
            'position': event['position']
        }))
    
    async def row_updated(self, event):
        """Handle row update events"""
        # Check if client is subscribed to this event
        if not hasattr(self, 'subscribed_events') or 'row_updated' not in self.subscribed_events:
            return
        
        # Check permissions for this specific row
        if not await self.check_row_permission(event['row_id']):
            return
        
        await self.send(text_data=json.dumps({
            'type': 'row_updated',
            'table_id': self.table_id,
            'row_id': event['row_id'],
            'data': event['data'],
            'user_id': event['user_id']
        }))
    
    @database_sync_to_async
    def check_table_permission(self):
        """Check if user has permission to access table"""
        from baserow.contrib.database.models import Table
        try:
            table = Table.objects.get(id=self.table_id)
            return table.has_user_permission(self.user, 'view')
        except Table.DoesNotExist:
            return False
```

## 📊 Data Flow Architecture

### Request Flow

```
1. Client Request
   ↓
2. Load Balancer (Nginx)
   ↓
3. Django Application
   ├── Authentication Middleware
   ├── Permission Middleware
   ├── Rate Limiting Middleware
   └── CORS Middleware
   ↓
4. URL Routing
   ↓
5. ViewSet/APIView
   ├── Permission Check
   ├── Serializer Validation
   └── Business Logic
   ↓
6. Model Layer
   ├── Database Query
   ├── Cache Check/Update
   └── File Operations
   ↓
7. Response Serialization
   ↓
8. Client Response
```

### Real-time Update Flow

```
1. Database Change (Create/Update/Delete)
   ↓
2. Django Signal Handler
   ↓
3. WebSocket Message Preparation
   ├── Permission Filtering
   ├── Data Serialization
   └── Event Routing
   ↓
4. Channel Layer (Redis)
   ↓
5. WebSocket Consumer
   ├── Client Filtering
   ├── Permission Re-check
   └── Message Formatting
   ↓
6. Client WebSocket Handler
   ├── State Update
   ├── UI Re-render
   └── Optimistic Updates
```

### Automation Flow

```
1. Trigger Event
   ├── Field Change
   ├── Time-based
   ├── External Webhook
   └── Manual Trigger
   ↓
2. Automation Engine
   ├── Trigger Evaluation
   ├── Condition Checking
   └── Action Queuing
   ↓
3. Celery Task Queue
   ├── Task Scheduling
   ├── Retry Logic
   └── Error Handling
   ↓
4. Action Execution
   ├── Field Updates
   ├── Notifications
   ├── External API Calls
   └── Webhook Delivery
   ↓
5. Result Logging
   ├── Success/Failure
   ├── Performance Metrics
   └── Audit Trail
```

## 🔧 Performance Architecture

### Caching Strategy

```python
# Multi-level caching implementation
class BaserowCache:
    """Centralized caching with multiple levels"""
    
    def __init__(self):
        self.memory_cache = {}  # In-memory cache
        self.redis_cache = redis.Redis()  # Redis cache
        self.cdn_cache = None  # CDN cache (CloudFlare, etc.)
    
    def get(self, key, level='redis'):
        """Get value from appropriate cache level"""
        if level == 'memory' and key in self.memory_cache:
            return self.memory_cache[key]
        
        if level in ['redis', 'memory']:
            value = self.redis_cache.get(key)
            if value and level == 'memory':
                self.memory_cache[key] = value
            return value
        
        return None
    
    def set(self, key, value, ttl=300, level='redis'):
        """Set value in appropriate cache level"""
        if level == 'memory':
            self.memory_cache[key] = value
        
        if level in ['redis', 'memory']:
            self.redis_cache.setex(key, ttl, value)
    
    def invalidate_pattern(self, pattern):
        """Invalidate cache keys matching pattern"""
        keys = self.redis_cache.keys(pattern)
        if keys:
            self.redis_cache.delete(*keys)
        
        # Clear memory cache items matching pattern
        to_remove = [k for k in self.memory_cache.keys() if fnmatch(k, pattern)]
        for key in to_remove:
            del self.memory_cache[key]

# Cache decorators for common patterns
def cache_table_data(ttl=300):
    """Decorator for caching table data"""
    def decorator(func):
        def wrapper(self, table_id, *args, **kwargs):
            cache_key = f"table_data:{table_id}:{hash(str(args) + str(kwargs))}"
            
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            result = func(self, table_id, *args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
```

### Database Optimization

```python
# Optimized querysets with select_related and prefetch_related
class OptimizedTableViewSet(viewsets.ModelViewSet):
    """Optimized table operations"""
    
    def get_queryset(self):
        """Optimized queryset with proper joins"""
        return Table.objects.select_related(
            'database',
            'database__workspace'
        ).prefetch_related(
            'fields',
            'views',
            'views__filters',
            'views__sortings'
        )
    
    def get_rows(self, table_id):
        """Optimized row fetching with pagination"""
        table = self.get_object()
        model_class = table.get_model()
        
        # Use database-level pagination for large datasets
        queryset = model_class.objects.all()
        
        # Apply select_related for foreign key fields
        foreign_key_fields = [
            f.db_column for f in table.fields.all() 
            if f.field_type == 'link_to_table'
        ]
        if foreign_key_fields:
            queryset = queryset.select_related(*foreign_key_fields)
        
        return queryset

# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'baserow',
        'USER': 'baserow',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        },
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

## 🔒 Security Architecture

### Authentication & Authorization

```python
# Multi-factor authentication
class MFAAuthenticationBackend:
    """Multi-factor authentication backend"""
    
    def authenticate(self, request, username=None, password=None, mfa_token=None):
        try:
            user = User.objects.get(username=username)
            
            # Check password
            if not user.check_password(password):
                return None
            
            # Check MFA if enabled
            if user.mfa_enabled:
                if not mfa_token:
                    raise MFARequired("MFA token required")
                
                if not self.verify_mfa_token(user, mfa_token):
                    return None
            
            return user
            
        except User.DoesNotExist:
            return None
    
    def verify_mfa_token(self, user, token):
        """Verify TOTP or SMS token"""
        if user.mfa_method == 'totp':
            return self.verify_totp(user, token)
        elif user.mfa_method == 'sms':
            return self.verify_sms(user, token)
        return False

# Row-level security with PostgreSQL RLS
class RowLevelSecurity:
    """PostgreSQL Row Level Security implementation"""
    
    @staticmethod
    def enable_rls(table_name):
        """Enable RLS on a table"""
        with connection.cursor() as cursor:
            cursor.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")
    
    @staticmethod
    def create_policy(table_name, policy_name, condition):
        """Create RLS policy"""
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE POLICY {policy_name} ON {table_name}
                FOR ALL TO baserow_users
                USING ({condition})
            """)
    
    @staticmethod
    def set_user_context(user_id, workspace_id):
        """Set user context for RLS"""
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL app.current_user_id = %s", [user_id])
            cursor.execute("SET LOCAL app.current_workspace_id = %s", [workspace_id])
```

## 📱 Mobile Architecture

### Progressive Web App (PWA)

```javascript
// Service Worker for offline functionality
// sw.js
const CACHE_NAME = 'baserow-v2.0.0'
const STATIC_CACHE = 'baserow-static-v2.0.0'
const API_CACHE = 'baserow-api-v2.0.0'

// Cache strategies
const cacheStrategies = {
  static: 'cache-first',
  api: 'network-first',
  images: 'cache-first'
}

self.addEventListener('install', event => {
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE).then(cache => {
        return cache.addAll([
          '/',
          '/manifest.json',
          '/css/app.css',
          '/js/app.js',
          '/icons/icon-192.png'
        ])
      }),
      
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  )
})

self.addEventListener('fetch', event => {
  const { request } = event
  const url = new URL(request.url)
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request))
  }
  // Handle static assets
  else if (request.destination === 'image') {
    event.respondWith(handleImageRequest(request))
  }
  // Handle app shell
  else {
    event.respondWith(handleAppShellRequest(request))
  }
})

async function handleApiRequest(request) {
  const cache = await caches.open(API_CACHE)
  
  try {
    // Try network first
    const response = await fetch(request)
    
    // Cache successful responses
    if (response.ok) {
      cache.put(request, response.clone())
    }
    
    return response
  } catch (error) {
    // Fallback to cache
    const cachedResponse = await cache.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline page for failed requests
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'This request requires an internet connection'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}
```

### Offline Data Synchronization

```javascript
// Offline sync manager
class OfflineSyncManager {
  constructor() {
    this.db = null
    this.syncQueue = []
    this.isOnline = navigator.onLine
    
    this.initDB()
    this.setupEventListeners()
  }
  
  async initDB() {
    // Initialize IndexedDB for offline storage
    this.db = await this.openDB('baserow-offline', 1, {
      upgrade(db) {
        // Tables store
        const tablesStore = db.createObjectStore('tables', { keyPath: 'id' })
        tablesStore.createIndex('workspace_id', 'workspace_id')
        
        // Rows store
        const rowsStore = db.createObjectStore('rows', { keyPath: 'id' })
        rowsStore.createIndex('table_id', 'table_id')
        
        // Sync queue store
        const syncStore = db.createObjectStore('sync_queue', { 
          keyPath: 'id', 
          autoIncrement: true 
        })
        syncStore.createIndex('timestamp', 'timestamp')
      }
    })
  }
  
  setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true
      this.processSyncQueue()
    })
    
    window.addEventListener('offline', () => {
      this.isOnline = false
    })
  }
  
  async saveOffline(type, data, action = 'create') {
    const tx = this.db.transaction([type, 'sync_queue'], 'readwrite')
    
    // Save data locally
    await tx.objectStore(type).put(data)
    
    // Add to sync queue
    await tx.objectStore('sync_queue').add({
      type,
      action,
      data,
      timestamp: Date.now(),
      synced: false
    })
    
    await tx.done
  }
  
  async processSyncQueue() {
    if (!this.isOnline) return
    
    const tx = this.db.transaction('sync_queue', 'readonly')
    const unsynced = await tx.store.index('timestamp').getAll()
    
    for (const item of unsynced.filter(i => !i.synced)) {
      try {
        await this.syncItem(item)
        await this.markSynced(item.id)
      } catch (error) {
        console.error('Sync failed for item:', item, error)
        // Implement exponential backoff for retries
      }
    }
  }
  
  async syncItem(item) {
    const { type, action, data } = item
    
    switch (action) {
      case 'create':
        return await api.post(`/${type}/`, data)
      case 'update':
        return await api.patch(`/${type}/${data.id}/`, data)
      case 'delete':
        return await api.delete(`/${type}/${data.id}/`)
    }
  }
}
```

This comprehensive architecture documentation covers all the major components and design decisions in the Baserow expansion. The system is designed to be scalable, maintainable, and performant while providing a rich user experience across all platforms.

## 🔗 Related Documentation

- [Frontend Development Guide](frontend.md) - Detailed Vue.js development
- [Backend Development Guide](backend.md) - Django development patterns
- [Database Schema](database.md) - Complete database structure
- [API Documentation](../api/overview.md) - REST API reference
- [Deployment Guide](deployment.md) - Production deployment

---

**Next Steps**: Dive into specific development guides or explore the [API documentation](../api/overview.md) for integration details.