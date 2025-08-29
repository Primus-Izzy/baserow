from django.db import migrations


class Migration(migrations.Migration):
    
    dependencies = [
        ('database', '0204_notification_system'),
    ]
    
    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS database_zapier_integration (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                group_id INTEGER NOT NULL,
                table_id INTEGER NOT NULL,
                integration_type VARCHAR(20) NOT NULL,
                trigger_type VARCHAR(50) NULL,
                action_type VARCHAR(50) NULL,
                configuration JSONB DEFAULT '{}',
                is_active BOOLEAN DEFAULT TRUE,
                created_by_id INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                total_executions INTEGER DEFAULT 0,
                successful_executions INTEGER DEFAULT 0,
                failed_executions INTEGER DEFAULT 0,
                last_execution_at TIMESTAMP WITH TIME ZONE NULL
            );
            
            CREATE TABLE IF NOT EXISTS database_zapier_execution (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                integration_id UUID NOT NULL,
                zapier_execution_id VARCHAR(255) NULL,
                input_data JSONB NOT NULL,
                output_data JSONB DEFAULT '{}',
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT DEFAULT '',
                execution_time_ms INTEGER NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE NULL
            );
            
            CREATE TABLE IF NOT EXISTS database_make_integration (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                group_id INTEGER NOT NULL,
                table_id INTEGER NOT NULL,
                module_type VARCHAR(20) NOT NULL,
                webhook_type VARCHAR(20) DEFAULT 'instant',
                webhook_url VARCHAR(2000) NULL,
                configuration JSONB DEFAULT '{}',
                is_active BOOLEAN DEFAULT TRUE,
                created_by_id INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                total_executions INTEGER DEFAULT 0,
                successful_executions INTEGER DEFAULT 0,
                failed_executions INTEGER DEFAULT 0,
                last_execution_at TIMESTAMP WITH TIME ZONE NULL
            );
            
            CREATE TABLE IF NOT EXISTS database_make_execution (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                integration_id UUID NOT NULL,
                make_execution_id VARCHAR(255) NULL,
                input_data JSONB NOT NULL,
                output_data JSONB DEFAULT '{}',
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT DEFAULT '',
                execution_time_ms INTEGER NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE NULL
            );
            
            CREATE INDEX IF NOT EXISTS idx_zapier_integration_group ON database_zapier_integration(group_id);
            CREATE INDEX IF NOT EXISTS idx_zapier_integration_table ON database_zapier_integration(table_id);
            CREATE INDEX IF NOT EXISTS idx_zapier_execution_integration ON database_zapier_execution(integration_id);
            CREATE INDEX IF NOT EXISTS idx_make_integration_group ON database_make_integration(group_id);
            CREATE INDEX IF NOT EXISTS idx_make_integration_table ON database_make_integration(table_id);
            CREATE INDEX IF NOT EXISTS idx_make_execution_integration ON database_make_execution(integration_id);
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS database_zapier_integration CASCADE;
            DROP TABLE IF EXISTS database_zapier_execution CASCADE;
            DROP TABLE IF EXISTS database_make_integration CASCADE;
            DROP TABLE IF EXISTS database_make_execution CASCADE;
            """
        ),
    ]