"""
Management command to initialize the granular permission system.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from baserow.contrib.database.permissions.handler import GranularPermissionHandler
from baserow.contrib.database.permissions.models import CustomRole, PermissionLevel
from baserow.core.models import Workspace


class Command(BaseCommand):
    """Initialize granular permission system with default roles."""
    
    help = "Initialize granular permission system with default roles"
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--workspace-id",
            type=int,
            help="Initialize permissions for specific workspace ID"
        )
        parser.add_argument(
            "--create-default-roles",
            action="store_true",
            help="Create default roles in all workspaces"
        )
    
    def handle(self, *args, **options):
        """Handle command execution."""
        workspace_id = options.get("workspace_id")
        create_default_roles = options.get("create_default_roles")
        
        handler = GranularPermissionHandler()
        
        if workspace_id:
            try:
                workspace = Workspace.objects.get(id=workspace_id)
                self.init_workspace_permissions(handler, workspace)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully initialized permissions for workspace {workspace.name}"
                    )
                )
            except Workspace.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Workspace with ID {workspace_id} not found")
                )
                return
        
        if create_default_roles:
            self.create_default_roles(handler)
            self.stdout.write(
                self.style.SUCCESS("Successfully created default roles in all workspaces")
            )
        
        if not workspace_id and not create_default_roles:
            self.stdout.write(
                self.style.WARNING(
                    "No action specified. Use --workspace-id or --create-default-roles"
                )
            )
    
    def init_workspace_permissions(self, handler: GranularPermissionHandler, workspace: Workspace):
        """Initialize permissions for a specific workspace."""
        with transaction.atomic():
            # Create default roles if they don't exist
            self.create_workspace_default_roles(handler, workspace)
            
            self.stdout.write(f"Initialized permissions for workspace: {workspace.name}")
    
    def create_default_roles(self, handler: GranularPermissionHandler):
        """Create default roles in all workspaces."""
        workspaces = Workspace.objects.all()
        
        for workspace in workspaces:
            with transaction.atomic():
                self.create_workspace_default_roles(handler, workspace)
                self.stdout.write(f"Created default roles for workspace: {workspace.name}")
    
    def create_workspace_default_roles(self, handler: GranularPermissionHandler, workspace: Workspace):
        """Create default roles for a workspace."""
        # Get workspace admin (first admin user)
        admin_user = workspace.workspaceuser_set.filter(
            permissions="ADMIN"
        ).first()
        
        if not admin_user:
            self.stdout.write(
                self.style.WARNING(f"No admin found for workspace {workspace.name}")
            )
            return
        
        admin_user = admin_user.user
        
        # Default roles to create
        default_roles = [
            {
                "name": "Editor",
                "description": "Can create, read, and update data but cannot delete",
                "can_create_tables": False,
                "can_delete_tables": False,
                "can_create_views": True,
                "can_manage_workspace": False,
            },
            {
                "name": "Viewer",
                "description": "Can only view data, cannot make changes",
                "can_create_tables": False,
                "can_delete_tables": False,
                "can_create_views": False,
                "can_manage_workspace": False,
            },
            {
                "name": "Commenter",
                "description": "Can view data and add comments",
                "can_create_tables": False,
                "can_delete_tables": False,
                "can_create_views": False,
                "can_manage_workspace": False,
            },
            {
                "name": "Table Manager",
                "description": "Can manage tables and their structure",
                "can_create_tables": True,
                "can_delete_tables": True,
                "can_create_views": True,
                "can_manage_workspace": False,
            },
        ]
        
        for role_data in default_roles:
            try:
                role = handler.create_custom_role(
                    workspace=workspace,
                    created_by=admin_user,
                    **role_data
                )
                self.stdout.write(f"  Created role: {role.name}")
            except Exception as e:
                # Role might already exist
                self.stdout.write(
                    self.style.WARNING(f"  Role {role_data['name']} already exists or error: {e}")
                )