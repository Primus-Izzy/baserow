from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from django.db import transaction
from django.db.models import Q

from baserow.contrib.database.fields.models import Field
from baserow.contrib.database.fields.registries import field_type_registry
from baserow.contrib.database.rows.handler import RowHandler
from baserow.contrib.database.views.models import (
    TimelineView,
    TimelineDependency,
    TimelineMilestone,
)


class TimelineViewHandler:
    """
    Handler for Timeline/Gantt view operations including dependency management
    and automatic schedule recalculation.
    """

    def create_dependency(
        self,
        timeline_view: TimelineView,
        predecessor_row_id: int,
        successor_row_id: int,
        dependency_type: str = TimelineDependency.DEPENDENCY_TYPE_CHOICES.FINISH_TO_START,
        lag_days: int = 0,
    ) -> TimelineDependency:
        """
        Creates a new dependency between two tasks.
        
        :param timeline_view: The timeline view instance
        :param predecessor_row_id: ID of the task that must be completed first
        :param successor_row_id: ID of the task that depends on the predecessor
        :param dependency_type: Type of dependency relationship
        :param lag_days: Number of days to wait after dependency is met
        :return: The created dependency
        :raises ValueError: If the dependency would create a circular reference
        """
        # Validate that tasks are not the same
        if predecessor_row_id == successor_row_id:
            raise ValueError("A task cannot depend on itself")

        # Check for circular dependencies
        if self._would_create_circular_dependency(
            timeline_view, predecessor_row_id, successor_row_id
        ):
            raise ValueError("Creating this dependency would result in a circular dependency")

        # Create the dependency
        dependency = TimelineDependency.objects.create(
            timeline_view=timeline_view,
            predecessor_row_id=predecessor_row_id,
            successor_row_id=successor_row_id,
            dependency_type=dependency_type,
            lag_days=lag_days,
        )

        # If auto-reschedule is enabled, recalculate the schedule
        if timeline_view.auto_reschedule:
            self.recalculate_schedule(
                timeline_view=timeline_view,
                changed_row_id=predecessor_row_id,
            )

        return dependency

    def delete_dependency(
        self,
        timeline_view: TimelineView,
        dependency_id: int,
    ) -> None:
        """
        Deletes a dependency between two tasks.
        
        :param timeline_view: The timeline view instance
        :param dependency_id: ID of the dependency to delete
        :raises ValueError: If the dependency doesn't exist
        """
        try:
            dependency = TimelineDependency.objects.get(
                id=dependency_id,
                timeline_view=timeline_view
            )
            dependency.delete()
        except TimelineDependency.DoesNotExist:
            raise ValueError("Dependency not found")

    def create_milestone(
        self,
        timeline_view: TimelineView,
        name: str,
        date_field_id: int,
        row_id: Optional[int] = None,
        color: str = "#FF0000",
        icon: str = "",
        description: str = "",
        is_active: bool = True,
    ) -> TimelineMilestone:
        """
        Creates a new milestone in the timeline view.
        
        :param timeline_view: The timeline view instance
        :param name: Name of the milestone
        :param date_field_id: ID of the date field that determines the milestone date
        :param row_id: Optional row ID if milestone is tied to a specific row
        :param color: Color for the milestone indicator
        :param icon: Icon name for the milestone indicator
        :param description: Optional description for the milestone
        :param is_active: Whether this milestone is currently active
        :return: The created milestone
        :raises ValueError: If the date field is invalid
        """
        # Validate the date field
        try:
            date_field = Field.objects.get(
                id=date_field_id,
                table=timeline_view.table
            )
            field_type = field_type_registry.get_by_model(date_field.specific_class)
            if not field_type.can_represent_date(date_field):
                raise ValueError("The specified field is not a valid date field")
        except Field.DoesNotExist:
            raise ValueError("The specified date field does not exist")

        milestone = TimelineMilestone.objects.create(
            timeline_view=timeline_view,
            name=name,
            date_field=date_field,
            row_id=row_id,
            color=color,
            icon=icon,
            description=description,
            is_active=is_active,
        )

        return milestone

    def recalculate_schedule(
        self,
        timeline_view: TimelineView,
        changed_row_id: int,
        new_start_date: Optional[datetime] = None,
        new_end_date: Optional[datetime] = None,
    ) -> List[int]:
        """
        Recalculates the schedule for dependent tasks when a task's dates change.
        
        :param timeline_view: The timeline view instance
        :param changed_row_id: ID of the row whose schedule changed
        :param new_start_date: New start date for the task (optional)
        :param new_end_date: New end date for the task (optional)
        :return: List of row IDs that were updated
        """
        if not timeline_view.enable_dependencies or not timeline_view.auto_reschedule:
            return []

        updated_rows = []
        
        with transaction.atomic():
            # Get all dependencies where this row is a predecessor
            dependencies = TimelineDependency.objects.filter(
                timeline_view=timeline_view,
                predecessor_row_id=changed_row_id
            ).select_related('timeline_view')

            # Get the table model
            model = timeline_view.table.get_model()
            
            # Get the changed row's current dates
            try:
                changed_row = model.objects.get(id=changed_row_id)
                predecessor_start_date = self._get_row_date(
                    changed_row, timeline_view.start_date_field
                )
                predecessor_end_date = self._get_row_date(
                    changed_row, timeline_view.end_date_field
                )
            except model.DoesNotExist:
                return []

            # Use provided dates if available
            if new_start_date:
                predecessor_start_date = new_start_date
            if new_end_date:
                predecessor_end_date = new_end_date

            if not predecessor_start_date or not predecessor_end_date:
                return []

            # Process each dependency
            for dependency in dependencies:
                try:
                    successor_row = model.objects.get(id=dependency.successor_row_id)
                    
                    # Calculate new dates based on dependency type
                    new_successor_dates = self._calculate_successor_dates(
                        dependency,
                        predecessor_start_date,
                        predecessor_end_date,
                        successor_row,
                        timeline_view
                    )
                    
                    if new_successor_dates:
                        # Update the successor row
                        row_handler = RowHandler()
                        update_values = {}
                        
                        if new_successor_dates.get('start_date'):
                            start_field_name = f"field_{timeline_view.start_date_field.id}"
                            update_values[start_field_name] = new_successor_dates['start_date']
                        
                        if new_successor_dates.get('end_date'):
                            end_field_name = f"field_{timeline_view.end_date_field.id}"
                            update_values[end_field_name] = new_successor_dates['end_date']
                        
                        if update_values:
                            row_handler.update_row_by_id(
                                user=None,  # System update
                                table=timeline_view.table,
                                row_id=dependency.successor_row_id,
                                values=update_values,
                            )
                            updated_rows.append(dependency.successor_row_id)
                            
                            # Recursively update dependencies of this row
                            recursive_updates = self.recalculate_schedule(
                                timeline_view=timeline_view,
                                changed_row_id=dependency.successor_row_id,
                                new_start_date=new_successor_dates.get('start_date'),
                                new_end_date=new_successor_dates.get('end_date'),
                            )
                            updated_rows.extend(recursive_updates)
                
                except model.DoesNotExist:
                    continue

        return list(set(updated_rows))  # Remove duplicates

    def get_dependency_chain(
        self,
        timeline_view: TimelineView,
        row_id: int,
    ) -> Dict[str, List[int]]:
        """
        Gets the dependency chain for a specific row.
        
        :param timeline_view: The timeline view instance
        :param row_id: ID of the row to analyze
        :return: Dictionary with 'predecessors' and 'successors' lists
        """
        predecessors = list(
            TimelineDependency.objects.filter(
                timeline_view=timeline_view,
                successor_row_id=row_id
            ).values_list('predecessor_row_id', flat=True)
        )
        
        successors = list(
            TimelineDependency.objects.filter(
                timeline_view=timeline_view,
                predecessor_row_id=row_id
            ).values_list('successor_row_id', flat=True)
        )
        
        return {
            'predecessors': predecessors,
            'successors': successors,
        }

    def _would_create_circular_dependency(
        self,
        timeline_view: TimelineView,
        predecessor_row_id: int,
        successor_row_id: int,
    ) -> bool:
        """
        Checks if creating a dependency would result in a circular reference.
        
        :param timeline_view: The timeline view instance
        :param predecessor_row_id: ID of the proposed predecessor
        :param successor_row_id: ID of the proposed successor
        :return: True if it would create a circular dependency
        """
        # Check if the successor is already a predecessor of the predecessor
        # (direct or indirect)
        visited = set()
        
        def has_path(from_row: int, to_row: int) -> bool:
            if from_row in visited:
                return False
            visited.add(from_row)
            
            # Direct dependency
            if TimelineDependency.objects.filter(
                timeline_view=timeline_view,
                predecessor_row_id=from_row,
                successor_row_id=to_row
            ).exists():
                return True
            
            # Indirect dependency through other rows
            successors = TimelineDependency.objects.filter(
                timeline_view=timeline_view,
                predecessor_row_id=from_row
            ).values_list('successor_row_id', flat=True)
            
            for successor in successors:
                if has_path(successor, to_row):
                    return True
            
            return False
        
        return has_path(successor_row_id, predecessor_row_id)

    def _get_row_date(self, row, date_field: Field) -> Optional[datetime]:
        """
        Extracts a date value from a row for a specific date field.
        
        :param row: The row instance
        :param date_field: The date field
        :return: The date value or None
        """
        if not date_field:
            return None
        
        field_name = f"field_{date_field.id}"
        return getattr(row, field_name, None)

    def _calculate_successor_dates(
        self,
        dependency: TimelineDependency,
        predecessor_start_date: datetime,
        predecessor_end_date: datetime,
        successor_row,
        timeline_view: TimelineView,
    ) -> Optional[Dict[str, datetime]]:
        """
        Calculates new dates for a successor task based on dependency type.
        
        :param dependency: The dependency relationship
        :param predecessor_start_date: Start date of the predecessor task
        :param predecessor_end_date: End date of the predecessor task
        :param successor_row: The successor row instance
        :param timeline_view: The timeline view instance
        :return: Dictionary with new start and end dates, or None
        """
        current_start = self._get_row_date(successor_row, timeline_view.start_date_field)
        current_end = self._get_row_date(successor_row, timeline_view.end_date_field)
        
        if not current_start or not current_end:
            return None
        
        # Calculate task duration
        task_duration = current_end - current_start
        lag_delta = timedelta(days=dependency.lag_days)
        
        new_dates = {}
        
        if dependency.dependency_type == TimelineDependency.DEPENDENCY_TYPE_CHOICES.FINISH_TO_START:
            # Successor starts when predecessor finishes (plus lag)
            new_start = predecessor_end_date + lag_delta
            new_dates['start_date'] = new_start
            new_dates['end_date'] = new_start + task_duration
            
        elif dependency.dependency_type == TimelineDependency.DEPENDENCY_TYPE_CHOICES.START_TO_START:
            # Successor starts when predecessor starts (plus lag)
            new_start = predecessor_start_date + lag_delta
            new_dates['start_date'] = new_start
            new_dates['end_date'] = new_start + task_duration
            
        elif dependency.dependency_type == TimelineDependency.DEPENDENCY_TYPE_CHOICES.FINISH_TO_FINISH:
            # Successor finishes when predecessor finishes (plus lag)
            new_end = predecessor_end_date + lag_delta
            new_dates['end_date'] = new_end
            new_dates['start_date'] = new_end - task_duration
            
        elif dependency.dependency_type == TimelineDependency.DEPENDENCY_TYPE_CHOICES.START_TO_FINISH:
            # Successor finishes when predecessor starts (plus lag)
            new_end = predecessor_start_date + lag_delta
            new_dates['end_date'] = new_end
            new_dates['start_date'] = new_end - task_duration
        
        return new_dates

    def get_critical_path(self, timeline_view: TimelineView) -> List[int]:
        """
        Calculates the critical path for the timeline view.
        
        :param timeline_view: The timeline view instance
        :return: List of row IDs that form the critical path
        """
        # This is a simplified critical path calculation
        # In a full implementation, this would use more sophisticated algorithms
        
        # Get all dependencies
        dependencies = TimelineDependency.objects.filter(
            timeline_view=timeline_view
        )
        
        # Build a graph of dependencies
        graph = {}
        for dep in dependencies:
            if dep.predecessor_row_id not in graph:
                graph[dep.predecessor_row_id] = []
            graph[dep.predecessor_row_id].append(dep.successor_row_id)
        
        # Find the longest path (simplified approach)
        # This would need more sophisticated implementation for production
        critical_path = []
        
        # For now, return an empty list as this is a complex algorithm
        # that would require more detailed implementation
        return critical_path