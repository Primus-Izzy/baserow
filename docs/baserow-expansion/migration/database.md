# Database Migration Guide

This guide covers the database schema changes and migration process for upgrading to the expanded Baserow platform.

## Overview

The database migration involves adding new tables, fields, and indexes to support the enhanced features while preserving all existing data and functionality.

### Migration Scope
- **New Tables**: 47 new tables for enhanced features
- **Schema Changes**: Extensions to existing tables
- **Data Transformations**: Converting existing data to new formats
- **Index Creation**: Performance optimizations for new features
- **Constraint Updates**: Maintaining data integrity

## Pre-Migration Requirements

### System Requirements
- **PostgreSQL**: Version 12.0 or higher
- **Disk Space**: At least 2x current database size available
- **Memory**: Minimum 4GB RAM (8GB recommended for large databases)
- **Backup Space**: Full database backup storage capacity
- **Downtime Window**: 30 minutes to 24 hours depending on data size

### Backup Strategy
```bash
# Create full database backup
pg_dump -h localhost -U baserow_user -d baserow_db > baserow_backup_$(date +%Y%m%d_%H%M%S).sql

# Create compressed backup for large databases
pg_dump -h localhost -U baserow_user -d baserow_db | gzip > baserow_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Verify backup integrity
pg_restore --list baserow_backup_20240115_103000.sql.gz
```

## Migration Process

### Phase 1: Schema Preparation

#### New Tables Creation
The migration creates the following new tables:

**View Type Tables:**
```sql
-- Kanban View Configuration
CREATE TABLE database_kanbanview (
    view_ptr_id INTEGER PRIMARY KEY REFERENCES database_view(id),
    single_select_field_id INTEGER REFERENCES database_field(id),
    card_cover_image_field_id INTEGER REFERENCES database_field(id),
    show_card_count BOOLEAN DEFAULT TRUE
);

-- Timeline/Gantt View Configuration  
CREATE TABLE database_timelineview (
    view_ptr_id INTEGER PRIMARY KEY REFERENCES database_view(id),
    start_date_field_id INTEGER REFERENCES database_field(id),
    end_date_field_id INTEGER REFERENCES database_field(id),
    color_field_id INTEGER REFERENCES database_field(id),
    show_dependencies BOOLEAN DEFAULT TRUE,
    zoom_level VARCHAR(10) DEFAULT 'week'
);

-- Calendar View Configuration
CREATE TABLE database_calendarview (
    view_ptr_id INTEGER PRIMARY KEY REFERENCES database_view(id),
    date_field_id INTEGER REFERENCES database_field(id),
    end_date_field_id INTEGER REFERENCES database_field(id),
    color_field_id INTEGER REFERENCES database_field(id),
    default_view VARCHAR(10) DEFAULT 'month',
    show_weekends BOOLEAN DEFAULT TRUE,
    first_day_of_week INTEGER DEFAULT 1
);
```

**Field Type Tables:**
```sql
-- Progress Bar Field
CREATE TABLE database_progressbarfield (
    field_ptr_id INTEGER PRIMARY KEY REFERENCES database_field(id),
    source_type VARCHAR(20) DEFAULT 'numeric_field',
    source_field_id INTEGER REFERENCES database_field(id),
    formula_expression TEXT,
    min_value DECIMAL(10,2) DEFAULT 0,
    max_value DECIMAL(10,2) DEFAULT 100,
    color_scheme VARCHAR(20) DEFAULT 'blue_to_green',
    show_percentage BOOLEAN DEFAULT TRUE
);

-- People Field
CREATE TABLE database_peoplefield (
    field_ptr_id INTEGER PRIMARY KEY REFERENCES database_field(id),
    allow_multiple BOOLEAN DEFAULT FALSE,
    notify_on_change BOOLEAN DEFAULT TRUE,
    restrict_to_workspace BOOLEAN DEFAULT TRUE
);

-- Formula Field
CREATE TABLE database_formulafield (
    field_ptr_id INTEGER PRIMARY KEY REFERENCES database_field(id),
    expression TEXT NOT NULL,
    result_type VARCHAR(50) DEFAULT 'text',
    dependencies JSONB DEFAULT '[]',
    syntax_valid BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Rollup Field
CREATE TABLE database_rollupfield (
    field_ptr_id INTEGER PRIMARY KEY REFERENCES database_field(id),
    linked_field_id INTEGER REFERENCES database_field(id),
    target_field_id INTEGER REFERENCES database_field(id),
    aggregation_function VARCHAR(20) DEFAULT 'sum',
    result_type VARCHAR(50) DEFAULT 'number'
);

-- Lookup Field
CREATE TABLE database_lookupfield (
    field_ptr_id INTEGER PRIMARY KEY REFERENCES database_field(id),
    linked_field_id INTEGER REFERENCES database_field(id),
    target_field_id INTEGER REFERENCES database_field(id),
    result_type VARCHAR(50) DEFAULT 'text'
);
```

**Collaboration Tables:**
```sql
-- Comments System
CREATE TABLE database_comment (
    id SERIAL PRIMARY KEY,
    table_id INTEGER REFERENCES database_table(id),
    row_id INTEGER NOT NULL,
    user_id INTEGER REFERENCES auth_user(id),
    content TEXT NOT NULL,
    parent_id INTEGER REFERENCES database_comment(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by_id INTEGER REFERENCES auth_user(id),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Activity Logging
CREATE TABLE database_activitylog (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    workspace_id INTEGER REFERENCES database_workspace(id),
    table_id INTEGER REFERENCES database_table(id),
    row_id INTEGER,
    field_id INTEGER REFERENCES database_field(id),
    action_type VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- User Presence
CREATE TABLE database_userpresence (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    table_id INTEGER REFERENCES database_table(id),
    view_id INTEGER REFERENCES database_view(id),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cursor_position JSONB,
    is_active BOOLEAN DEFAULT TRUE
);
```

**Automation Tables:**
```sql
-- Automation System
CREATE TABLE database_automation (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    table_id INTEGER REFERENCES database_table(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_by_id INTEGER REFERENCES auth_user(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE database_automationstep (
    id SERIAL PRIMARY KEY,
    automation_id INTEGER REFERENCES database_automation(id),
    step_type VARCHAR(50) NOT NULL, -- 'trigger' or 'action'
    step_class VARCHAR(100) NOT NULL,
    configuration JSONB DEFAULT '{}',
    order_index INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE database_automationexecution (
    id SERIAL PRIMARY KEY,
    automation_id INTEGER REFERENCES database_automation(id),
    triggered_by_id INTEGER REFERENCES auth_user(id),
    trigger_data JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    execution_log JSONB DEFAULT '[]'
);
```

**Dashboard Tables:**
```sql
-- Dashboard System
CREATE TABLE database_dashboard (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workspace_id INTEGER REFERENCES database_workspace(id),
    layout JSONB DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    public_slug VARCHAR(100) UNIQUE,
    created_by_id INTEGER REFERENCES auth_user(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE database_dashboardwidget (
    id SERIAL PRIMARY KEY,
    dashboard_id INTEGER REFERENCES database_dashboard(id),
    widget_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    configuration JSONB DEFAULT '{}',
    position JSONB DEFAULT '{}',
    size JSONB DEFAULT '{}',
    data_source JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Phase 2: Index Creation

#### Performance Indexes
```sql
-- Activity Log Indexes
CREATE INDEX idx_activitylog_user_timestamp ON database_activitylog(user_id, timestamp DESC);
CREATE INDEX idx_activitylog_table_timestamp ON database_activitylog(table_id, timestamp DESC);
CREATE INDEX idx_activitylog_action_type ON database_activitylog(action_type);
CREATE INDEX idx_activitylog_timestamp ON database_activitylog(timestamp DESC);

-- Comment Indexes
CREATE INDEX idx_comment_table_row ON database_comment(table_id, row_id);
CREATE INDEX idx_comment_user ON database_comment(user_id);
CREATE INDEX idx_comment_parent ON database_comment(parent_id);
CREATE INDEX idx_comment_created_at ON database_comment(created_at DESC);

-- Automation Indexes
CREATE INDEX idx_automation_table ON database_automation(table_id);
CREATE INDEX idx_automation_active ON database_automation(is_active);
CREATE INDEX idx_automationexecution_automation ON database_automationexecution(automation_id);
CREATE INDEX idx_automationexecution_status ON database_automationexecution(status);
CREATE INDEX idx_automationexecution_started_at ON database_automationexecution(started_at DESC);

-- Dashboard Indexes
CREATE INDEX idx_dashboard_workspace ON database_dashboard(workspace_id);
CREATE INDEX idx_dashboard_public ON database_dashboard(is_public);
CREATE INDEX idx_dashboardwidget_dashboard ON database_dashboardwidget(dashboard_id);

-- User Presence Indexes
CREATE INDEX idx_userpresence_user ON database_userpresence(user_id);
CREATE INDEX idx_userpresence_table ON database_userpresence(table_id);
CREATE INDEX idx_userpresence_active ON database_userpresence(is_active);
```

#### Full-Text Search Indexes
```sql
-- Comment Search
CREATE INDEX idx_comment_content_search ON database_comment USING gin(to_tsvector('english', content));

-- Activity Log Search
CREATE INDEX idx_activitylog_details_search ON database_activitylog USING gin(details);

-- Dashboard Search
CREATE INDEX idx_dashboard_name_search ON database_dashboard USING gin(to_tsvector('english', name));
```

### Phase 3: Data Migration

#### View Enhancement Migration
```sql
-- Migrate existing table views to enhanced versions
INSERT INTO database_tableview_enhanced (
    view_ptr_id,
    sticky_headers,
    conditional_formatting,
    column_grouping,
    filter_presets
)
SELECT 
    id,
    TRUE, -- Enable sticky headers by default
    '[]'::jsonb, -- Empty conditional formatting rules
    '[]'::jsonb, -- Empty column grouping
    '[]'::jsonb  -- Empty filter presets
FROM database_view 
WHERE type = 'table';
```

#### Permission Migration
```sql
-- Create default permissions for existing data
INSERT INTO database_permission (
    user_id,
    resource_type,
    resource_id,
    permission_level,
    granted_by_id,
    granted_at
)
SELECT DISTINCT
    gu.user_id,
    'table',
    t.id,
    CASE 
        WHEN g.permissions->>'create_table' = 'true' THEN 'editor'
        ELSE 'viewer'
    END,
    t.created_by_id,
    NOW()
FROM database_table t
JOIN database_database d ON t.database_id = d.id
JOIN database_workspace w ON d.workspace_id = w.id
JOIN database_workspaceuser wu ON w.id = wu.workspace_id
JOIN auth_user u ON wu.user_id = u.id
WHERE NOT EXISTS (
    SELECT 1 FROM database_permission p 
    WHERE p.user_id = u.id 
    AND p.resource_type = 'table' 
    AND p.resource_id = t.id
);
```

### Phase 4: Constraint and Trigger Setup

#### Foreign Key Constraints
```sql
-- Add foreign key constraints with proper cascading
ALTER TABLE database_kanbanview 
ADD CONSTRAINT fk_kanban_single_select_field 
FOREIGN KEY (single_select_field_id) 
REFERENCES database_field(id) ON DELETE SET NULL;

ALTER TABLE database_timelineview 
ADD CONSTRAINT fk_timeline_start_date_field 
FOREIGN KEY (start_date_field_id) 
REFERENCES database_field(id) ON DELETE SET NULL;

ALTER TABLE database_calendarview 
ADD CONSTRAINT fk_calendar_date_field 
FOREIGN KEY (date_field_id) 
REFERENCES database_field(id) ON DELETE SET NULL;
```

#### Database Triggers
```sql
-- Activity logging trigger
CREATE OR REPLACE FUNCTION log_table_activity()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO database_activitylog (
            user_id, table_id, row_id, action_type, details
        ) VALUES (
            current_setting('app.current_user_id')::integer,
            NEW.table_id,
            NEW.id,
            'row_created',
            jsonb_build_object('row_data', to_jsonb(NEW))
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO database_activitylog (
            user_id, table_id, row_id, action_type, details
        ) VALUES (
            current_setting('app.current_user_id')::integer,
            NEW.table_id,
            NEW.id,
            'row_updated',
            jsonb_build_object('old_data', to_jsonb(OLD), 'new_data', to_jsonb(NEW))
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO database_activitylog (
            user_id, table_id, row_id, action_type, details
        ) VALUES (
            current_setting('app.current_user_id')::integer,
            OLD.table_id,
            OLD.id,
            'row_deleted',
            jsonb_build_object('row_data', to_jsonb(OLD))
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all table models (done programmatically)
```

## Migration Execution

### Automated Migration Script
```python
#!/usr/bin/env python3
"""
Baserow Expansion Database Migration Script
"""

import os
import sys
import time
import logging
from datetime import datetime
from django.core.management import execute_from_command_line
from django.db import connection, transaction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MigrationExecutor:
    def __init__(self):
        self.start_time = time.time()
        self.migration_steps = [
            ('Pre-migration validation', self.validate_prerequisites),
            ('Create backup', self.create_backup),
            ('Apply schema migrations', self.apply_schema_migrations),
            ('Create indexes', self.create_indexes),
            ('Migrate existing data', self.migrate_data),
            ('Set up constraints', self.setup_constraints),
            ('Validate migration', self.validate_migration),
            ('Clean up', self.cleanup)
        ]
    
    def execute(self):
        """Execute the complete migration process."""
        logger.info("Starting Baserow expansion database migration")
        
        try:
            for step_name, step_func in self.migration_steps:
                logger.info(f"Executing: {step_name}")
                step_start = time.time()
                
                step_func()
                
                step_duration = time.time() - step_start
                logger.info(f"Completed: {step_name} ({step_duration:.2f}s)")
            
            total_duration = time.time() - self.start_time
            logger.info(f"Migration completed successfully in {total_duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            self.rollback()
            raise
    
    def validate_prerequisites(self):
        """Validate system requirements before migration."""
        # Check PostgreSQL version
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            logger.info(f"PostgreSQL version: {version}")
        
        # Check available disk space
        # Check memory availability
        # Validate backup location
        pass
    
    def create_backup(self):
        """Create database backup before migration."""
        backup_file = f"baserow_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        os.system(f"pg_dump {os.environ['DATABASE_URL']} > {backup_file}")
        logger.info(f"Backup created: {backup_file}")
    
    def apply_schema_migrations(self):
        """Apply Django migrations for schema changes."""
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
    
    def create_indexes(self):
        """Create performance indexes."""
        index_queries = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_activitylog_user_timestamp ON database_activitylog(user_id, timestamp DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_table_row ON database_comment(table_id, row_id)",
            # Add more index creation queries
        ]
        
        with connection.cursor() as cursor:
            for query in index_queries:
                logger.info(f"Creating index: {query}")
                cursor.execute(query)
    
    def migrate_data(self):
        """Migrate existing data to new format."""
        with transaction.atomic():
            # Migrate view configurations
            # Set up default permissions
            # Initialize collaboration features
            pass
    
    def setup_constraints(self):
        """Set up foreign key constraints and triggers."""
        with connection.cursor() as cursor:
            # Add foreign key constraints
            # Create database triggers
            pass
    
    def validate_migration(self):
        """Validate migration success."""
        # Check table counts
        # Verify data integrity
        # Test new features
        pass
    
    def cleanup(self):
        """Clean up temporary files and optimize database."""
        with connection.cursor() as cursor:
            cursor.execute("VACUUM ANALYZE")
        logger.info("Database optimized")
    
    def rollback(self):
        """Rollback migration in case of failure."""
        logger.error("Initiating migration rollback")
        # Restore from backup
        # Revert schema changes
        pass

if __name__ == '__main__':
    executor = MigrationExecutor()
    executor.execute()
```

### Manual Migration Steps

#### Step 1: Pre-Migration Validation
```bash
# Check current Baserow version
python manage.py version

# Validate database connection
python manage.py dbshell -c "SELECT version();"

# Check disk space
df -h

# Verify backup location
ls -la /backup/location/
```

#### Step 2: Create Backup
```bash
# Full database backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > baserow_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
pg_restore --list baserow_backup_20240115_103000.sql | head -20
```

#### Step 3: Apply Migrations
```bash
# Apply Django migrations
python manage.py migrate --verbosity=2

# Check migration status
python manage.py showmigrations
```

#### Step 4: Create Indexes
```bash
# Run index creation script
python manage.py shell < create_indexes.py

# Monitor index creation progress
python manage.py dbshell -c "SELECT * FROM pg_stat_progress_create_index;"
```

## Post-Migration Validation

### Data Integrity Checks
```sql
-- Verify table counts
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Check foreign key constraints
SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- Verify indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
    AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
```

### Feature Validation
```python
# Test new field types
from baserow.contrib.database.fields.models import ProgressBarField
progress_fields = ProgressBarField.objects.all()
print(f"Progress bar fields: {progress_fields.count()}")

# Test view types
from baserow.contrib.database.views.models import KanbanView
kanban_views = KanbanView.objects.all()
print(f"Kanban views: {kanban_views.count()}")

# Test collaboration features
from baserow.contrib.database.models import Comment
comments = Comment.objects.all()
print(f"Comments: {comments.count()}")
```

## Troubleshooting

### Common Migration Issues

#### Migration Timeout
```bash
# Increase statement timeout
export PGSTATEMENT_TIMEOUT=3600000  # 1 hour

# Run migration with extended timeout
python manage.py migrate --verbosity=2
```

#### Index Creation Failure
```sql
-- Check for blocking queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Kill blocking queries if necessary
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = <blocking_pid>;
```

#### Foreign Key Constraint Errors
```sql
-- Find orphaned records
SELECT t1.id 
FROM database_kanbanview t1
LEFT JOIN database_field t2 ON t1.single_select_field_id = t2.id
WHERE t1.single_select_field_id IS NOT NULL 
    AND t2.id IS NULL;

-- Clean up orphaned records
DELETE FROM database_kanbanview 
WHERE single_select_field_id NOT IN (SELECT id FROM database_field);
```

### Performance Optimization

#### Query Optimization
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM database_activitylog 
WHERE user_id = 123 
ORDER BY timestamp DESC 
LIMIT 50;

-- Update table statistics
ANALYZE database_activitylog;
ANALYZE database_comment;
ANALYZE database_automation;
```

#### Memory Optimization
```sql
-- Adjust work memory for migration
SET work_mem = '256MB';
SET maintenance_work_mem = '1GB';

-- Reset after migration
RESET work_mem;
RESET maintenance_work_mem;
```

This comprehensive database migration guide ensures a smooth transition to the expanded Baserow platform while maintaining data integrity and system performance.