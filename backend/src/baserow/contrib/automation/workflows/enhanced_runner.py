"""
Enhanced automation workflow runner with support for multi-step workflows,
conditional branching, error handling, and retry logic.
"""

import logging
import time
import uuid
from typing import TYPE_CHECKING, Type, Dict, Any, List, Optional

from django.utils import timezone
from django.db import transaction

from baserow.contrib.automation.automation_dispatch_context import (
    AutomationDispatchContext,
)
from baserow.contrib.automation.nodes.exceptions import (
    AutomationNodeMisconfiguredService,
)
from baserow.contrib.automation.nodes.node_types import AutomationNodeActionNodeType
from baserow.contrib.automation.nodes.enhanced_action_models import WorkflowExecutionLog
from baserow.contrib.automation.workflows.models import AutomationWorkflow
from baserow.core.services.exceptions import (
    ServiceImproperlyConfiguredDispatchException,
)

if TYPE_CHECKING:
    from baserow.contrib.automation.nodes.models import AutomationNode

logger = logging.getLogger(__name__)


class WorkflowExecutionContext:
    """
    Context for tracking workflow execution state and data flow.
    """
    
    def __init__(self, workflow: AutomationWorkflow, initial_data: Dict[str, Any]):
        self.workflow = workflow
        self.execution_id = str(uuid.uuid4())
        self.start_time = timezone.now()
        self.data = initial_data.copy()
        self.node_outputs = {}  # Store outputs from each node
        self.execution_path = []  # Track which nodes were executed
        self.errors = []  # Track any errors that occurred
        self.status = 'running'
    
    def add_node_output(self, node_id: int, output_data: Dict[str, Any]):
        """Add output data from a node execution."""
        self.node_outputs[node_id] = output_data
        self.execution_path.append(node_id)
    
    def add_error(self, node_id: int, error: Exception):
        """Add an error that occurred during execution."""
        self.errors.append({
            'node_id': node_id,
            'error': str(error),
            'timestamp': timezone.now()
        })
    
    def get_node_output(self, node_id: int) -> Dict[str, Any]:
        """Get output data from a specific node."""
        return self.node_outputs.get(node_id, {})
    
    def update_data(self, new_data: Dict[str, Any]):
        """Update the context data with new values."""
        self.data.update(new_data)


class EnhancedAutomationWorkflowRunner:
    """
    Enhanced automation workflow runner with support for:
    - Multi-step workflows with conditional branching
    - Comprehensive error handling and retry logic
    - Execution logging and monitoring
    - Sequential action processing
    """
    
    def __init__(self):
        self.max_execution_time = 300  # 5 minutes max execution time
        self.max_retry_attempts = 3
        self.retry_delay_base = 1  # Base delay in seconds
        self.retry_delay_multiplier = 2
    
    def run(
        self,
        workflow: AutomationWorkflow,
        dispatch_context: AutomationDispatchContext,
    ):
        """
        Run the automation workflow with enhanced error handling and logging.
        
        :param workflow: The automation workflow to run
        :param dispatch_context: The context in which the workflow is being dispatched
        """
        
        execution_context = WorkflowExecutionContext(
            workflow, dispatch_context.data
        )
        
        try:
            logger.info(
                f"Starting workflow execution {execution_context.execution_id} "
                f"for workflow {workflow.id}"
            )
            
            # Get the trigger node and start execution
            trigger_node = workflow.get_trigger()
            
            if not trigger_node:
                raise ValueError(f"Workflow {workflow.id} has no trigger node")
            
            # Execute the workflow starting from trigger's next nodes
            self._execute_workflow_branch(
                trigger_node.get_next_nodes(),
                execution_context,
                dispatch_context
            )
            
            execution_context.status = 'completed'
            
            logger.info(
                f"Completed workflow execution {execution_context.execution_id} "
                f"in {(timezone.now() - execution_context.start_time).total_seconds():.2f}s"
            )
            
        except Exception as e:
            execution_context.status = 'failed'
            execution_context.add_error(0, e)  # General workflow error
            
            logger.error(
                f"Workflow execution {execution_context.execution_id} failed: {e}",
                exc_info=True
            )
            
            # Log the failure
            self._log_workflow_execution(execution_context, str(e))
            
            raise
        
        finally:
            # Always log the execution result
            self._log_workflow_execution(execution_context)
    
    def _execute_workflow_branch(
        self,
        nodes: List["AutomationNode"],
        execution_context: WorkflowExecutionContext,
        dispatch_context: AutomationDispatchContext
    ):
        """
        Execute a branch of the workflow (list of nodes).
        
        :param nodes: List of nodes to execute
        :param execution_context: Workflow execution context
        :param dispatch_context: Automation dispatch context
        """
        
        for node in nodes:
            # Check execution timeout
            elapsed_time = (timezone.now() - execution_context.start_time).total_seconds()
            if elapsed_time > self.max_execution_time:
                raise TimeoutError(
                    f"Workflow execution exceeded maximum time limit of "
                    f"{self.max_execution_time} seconds"
                )
            
            # Execute the node with retry logic
            try:
                self._execute_node_with_retry(
                    node, execution_context, dispatch_context
                )
            except Exception as e:
                # Handle node execution failure
                execution_context.add_error(node.id, e)
                
                # Check if this is a critical error that should stop execution
                if self._is_critical_error(e):
                    raise
                
                # For non-critical errors, log and continue
                logger.warning(
                    f"Node {node.id} failed but continuing execution: {e}"
                )
    
    def _execute_node_with_retry(
        self,
        node: "AutomationNode",
        execution_context: WorkflowExecutionContext,
        dispatch_context: AutomationDispatchContext
    ):
        """
        Execute a single node with retry logic.
        
        :param node: Node to execute
        :param execution_context: Workflow execution context
        :param dispatch_context: Automation dispatch context
        """
        
        last_exception = None
        
        for attempt in range(self.max_retry_attempts):
            try:
                # Update dispatch context with latest data
                dispatch_context.data = execution_context.data
                
                # Execute the node
                dispatch_result = self._dispatch_node(node, dispatch_context)
                
                # Store the node output
                execution_context.add_node_output(node.id, dispatch_result.data)
                
                # Update context data with node output
                if dispatch_result.data:
                    execution_context.update_data(dispatch_result.data)
                
                # Get next nodes based on output
                next_nodes = node.get_next_nodes(dispatch_result.output_uid)
                
                # Recursively execute next nodes
                if next_nodes:
                    self._execute_workflow_branch(
                        list(next_nodes), execution_context, dispatch_context
                    )
                
                # Success - break retry loop
                break
                
            except Exception as e:
                last_exception = e
                
                # Log the retry attempt
                logger.warning(
                    f"Node {node.id} execution attempt {attempt + 1} failed: {e}"
                )
                
                # If this is the last attempt, re-raise the exception
                if attempt == self.max_retry_attempts - 1:
                    raise
                
                # Wait before retrying (exponential backoff)
                retry_delay = self.retry_delay_base * (self.retry_delay_multiplier ** attempt)
                time.sleep(retry_delay)
    
    def _dispatch_node(
        self, 
        node: "AutomationNode", 
        dispatch_context: AutomationDispatchContext
    ):
        """
        Dispatch a single node and handle service configuration errors.
        
        :param node: The node to dispatch
        :param dispatch_context: The dispatch context
        :return: Dispatch result
        """
        
        node_type: Type[AutomationNodeActionNodeType] = node.get_type()
        
        try:
            dispatch_result = node_type.dispatch(node, dispatch_context)
            dispatch_context.after_dispatch(node, dispatch_result)
            return dispatch_result
            
        except ServiceImproperlyConfiguredDispatchException as e:
            raise AutomationNodeMisconfiguredService(node.id) from e
    
    def _is_critical_error(self, error: Exception) -> bool:
        """
        Determine if an error is critical and should stop workflow execution.
        
        :param error: The exception that occurred
        :return: True if the error is critical
        """
        
        # Define critical error types
        critical_error_types = [
            TimeoutError,
            MemoryError,
            KeyboardInterrupt,
            SystemExit,
        ]
        
        return any(isinstance(error, error_type) for error_type in critical_error_types)
    
    def _log_workflow_execution(
        self, 
        execution_context: WorkflowExecutionContext,
        error_message: str = ""
    ):
        """
        Log the workflow execution details.
        
        :param execution_context: Workflow execution context
        :param error_message: Error message if execution failed
        """
        
        try:
            # Calculate execution time
            execution_time = (timezone.now() - execution_context.start_time).total_seconds()
            
            # Create a summary log entry for the entire workflow
            WorkflowExecutionLog.objects.create(
                workflow=execution_context.workflow,
                node_id=None,  # This is a workflow-level log
                execution_id=execution_context.execution_id,
                status=execution_context.status,
                input_data=execution_context.data,
                output_data={
                    'execution_path': execution_context.execution_path,
                    'node_outputs': execution_context.node_outputs,
                    'errors': execution_context.errors,
                },
                execution_time_ms=int(execution_time * 1000),
                error_message=error_message
            )
            
        except Exception as e:
            # Don't let logging errors break the workflow
            logger.error(f"Failed to log workflow execution: {e}")


class SequentialActionProcessor:
    """
    Processor for handling sequential action execution with proper ordering.
    """
    
    def __init__(self, runner: EnhancedAutomationWorkflowRunner):
        self.runner = runner
    
    def process_action_sequence(
        self,
        actions: List["AutomationNode"],
        execution_context: WorkflowExecutionContext,
        dispatch_context: AutomationDispatchContext
    ):
        """
        Process a sequence of actions in order, ensuring each completes
        before the next begins.
        
        :param actions: List of action nodes to execute in sequence
        :param execution_context: Workflow execution context
        :param dispatch_context: Automation dispatch context
        """
        
        for i, action in enumerate(actions):
            logger.debug(
                f"Processing action {i + 1}/{len(actions)}: {action.id}"
            )
            
            try:
                # Execute the action
                self.runner._execute_node_with_retry(
                    action, execution_context, dispatch_context
                )
                
                logger.debug(f"Completed action {action.id}")
                
            except Exception as e:
                logger.error(f"Action {action.id} failed: {e}")
                
                # Decide whether to continue or stop based on error handling policy
                if self._should_stop_on_error(action, e):
                    raise
                
                # Continue with next action
                continue
    
    def _should_stop_on_error(
        self, 
        action: "AutomationNode", 
        error: Exception
    ) -> bool:
        """
        Determine if the sequence should stop when an action fails.
        
        :param action: The action that failed
        :param error: The exception that occurred
        :return: True if the sequence should stop
        """
        
        # This could be configurable per action or workflow
        # For now, stop on critical errors only
        return self.runner._is_critical_error(error)


class ConditionalBranchProcessor:
    """
    Processor for handling conditional branching in workflows.
    """
    
    def __init__(self, runner: EnhancedAutomationWorkflowRunner):
        self.runner = runner
    
    def process_conditional_branch(
        self,
        condition_node: "AutomationNode",
        true_branch: List["AutomationNode"],
        false_branch: List["AutomationNode"],
        execution_context: WorkflowExecutionContext,
        dispatch_context: AutomationDispatchContext
    ):
        """
        Process a conditional branch by evaluating the condition and
        executing the appropriate branch.
        
        :param condition_node: Node that evaluates the condition
        :param true_branch: Nodes to execute if condition is true
        :param false_branch: Nodes to execute if condition is false
        :param execution_context: Workflow execution context
        :param dispatch_context: Automation dispatch context
        """
        
        # Execute the condition node
        dispatch_result = self.runner._dispatch_node(condition_node, dispatch_context)
        
        # Store the condition result
        execution_context.add_node_output(condition_node.id, dispatch_result.data)
        
        # Determine which branch to execute
        if dispatch_result.output_uid == 'true':
            logger.debug("Condition evaluated to true, executing true branch")
            self.runner._execute_workflow_branch(
                true_branch, execution_context, dispatch_context
            )
        else:
            logger.debug("Condition evaluated to false, executing false branch")
            self.runner._execute_workflow_branch(
                false_branch, execution_context, dispatch_context
            )