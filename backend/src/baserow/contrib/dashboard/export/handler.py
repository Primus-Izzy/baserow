from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from baserow.contrib.dashboard.models import Dashboard, DashboardExport
from baserow.contrib.dashboard.sharing.handler import dashboard_sharing_handler
from celery import shared_task
import logging
import json
import csv
import io
import os
from datetime import datetime, timedelta
import uuid

User = get_user_model()
logger = logging.getLogger(__name__)


class DashboardExportHandler:
    """Handler for dashboard export functionality."""
    
    def create_export_job(self, dashboard, user, export_format, configuration=None, 
                         delivery_email=None, schedule_config=None):
        """Create a new export job for a dashboard."""
        if not dashboard_sharing_handler.user_can_view_dashboard(dashboard, user):
            raise PermissionDenied("You don't have permission to export this dashboard")
        
        if export_format not in ['pdf', 'png', 'csv']:
            raise ValidationError("Invalid export format")
        
        export_job = DashboardExport.objects.create(
            dashboard=dashboard,
            requested_by=user,
            export_format=export_format,
            configuration=configuration or {},
            delivery_email=delivery_email,
            is_scheduled=bool(schedule_config),
            schedule_config=schedule_config or {}
        )
        
        if schedule_config:
            # Calculate next run time based on schedule
            export_job.next_run = self._calculate_next_run(schedule_config)
            export_job.save(update_fields=['next_run'])
        
        # Queue the export job
        process_dashboard_export.delay(str(export_job.id))
        
        return export_job
    
    def get_export_status(self, export_id, user):
        """Get the status of an export job."""
        try:
            export_job = DashboardExport.objects.get(id=export_id)
            
            # Check permissions
            if not dashboard_sharing_handler.user_can_view_dashboard(export_job.dashboard, user):
                raise PermissionDenied("You don't have permission to view this export")
            
            return {
                'id': str(export_job.id),
                'status': export_job.status,
                'format': export_job.export_format,
                'created_at': export_job.created_at,
                'completed_at': export_job.completed_at,
                'file_size': export_job.file_size,
                'download_url': self._get_download_url(export_job) if export_job.status == 'completed' else None,
                'error_message': export_job.error_message
            }
        except DashboardExport.DoesNotExist:
            raise ValidationError("Export job not found")
    
    def get_user_exports(self, user, dashboard_id=None):
        """Get all export jobs for a user, optionally filtered by dashboard."""
        queryset = DashboardExport.objects.filter(requested_by=user)
        
        if dashboard_id:
            queryset = queryset.filter(dashboard_id=dashboard_id)
        
        return queryset.order_by('-created_at')
    
    def cancel_export_job(self, export_id, user):
        """Cancel a pending export job."""
        try:
            export_job = DashboardExport.objects.get(id=export_id, requested_by=user)
            
            if export_job.status in ['pending', 'processing']:
                export_job.status = 'failed'
                export_job.error_message = 'Cancelled by user'
                export_job.save(update_fields=['status', 'error_message'])
                return True
            
            return False
        except DashboardExport.DoesNotExist:
            raise ValidationError("Export job not found")
    
    def delete_export_file(self, export_id, user):
        """Delete an export file."""
        try:
            export_job = DashboardExport.objects.get(id=export_id, requested_by=user)
            
            if export_job.file_path and default_storage.exists(export_job.file_path):
                default_storage.delete(export_job.file_path)
            
            export_job.delete()
            return True
        except DashboardExport.DoesNotExist:
            raise ValidationError("Export job not found")
    
    def _calculate_next_run(self, schedule_config):
        """Calculate the next run time based on schedule configuration."""
        now = timezone.now()
        
        if schedule_config.get('type') == 'daily':
            return now + timedelta(days=1)
        elif schedule_config.get('type') == 'weekly':
            return now + timedelta(weeks=1)
        elif schedule_config.get('type') == 'monthly':
            return now + timedelta(days=30)  # Simplified monthly calculation
        else:
            return now + timedelta(hours=1)  # Default to hourly
    
    def _get_download_url(self, export_job):
        """Generate a download URL for an export file."""
        if export_job.file_path:
            return f"{settings.PUBLIC_BACKEND_URL}/api/dashboard/exports/{export_job.id}/download/"
        return None
    
    def process_csv_export(self, dashboard, configuration):
        """Process CSV export for dashboard data."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Get dashboard widgets and their data
        widgets = dashboard.widgets.all()
        
        for widget in widgets:
            # Write widget header
            writer.writerow([f"Widget: {widget.widget_type}"])
            writer.writerow([])  # Empty row for spacing
            
            # Get widget data based on type
            widget_data = self._get_widget_data_for_csv(widget)
            
            if widget_data:
                # Write headers
                if widget_data.get('headers'):
                    writer.writerow(widget_data['headers'])
                
                # Write data rows
                for row in widget_data.get('rows', []):
                    writer.writerow(row)
            
            writer.writerow([])  # Empty row between widgets
        
        return output.getvalue()
    
    def _get_widget_data_for_csv(self, widget):
        """Extract data from a widget for CSV export."""
        # This would integrate with the actual widget data fetching logic
        # For now, return a placeholder structure
        return {
            'headers': ['Field', 'Value'],
            'rows': [
                ['Widget Type', widget.widget_type],
                ['Created', widget.created_at.strftime('%Y-%m-%d %H:%M:%S')],
                ['Configuration', json.dumps(widget.configuration)]
            ]
        }
    
    def _generate_pdf_export(self, dashboard, configuration):
        """Generate PDF export for dashboard."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4, A3
            from reportlab.lib.units import inch
            import io
            
            # Get page configuration
            page_size = configuration.get('pageSize', 'A4')
            orientation = configuration.get('orientation', 'landscape')
            
            # Set page size
            if page_size == 'A3':
                page_format = A3
            elif page_size == 'Letter':
                page_format = letter
            else:
                page_format = A4
            
            # Adjust for orientation
            if orientation == 'landscape':
                page_format = (page_format[1], page_format[0])
            
            # Create PDF buffer
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=page_format)
            
            # Add title if requested
            if configuration.get('include_title', True):
                p.setFont("Helvetica-Bold", 16)
                p.drawString(50, page_format[1] - 50, f"Dashboard: {dashboard.name}")
            
            # Add timestamp if requested
            if configuration.get('include_timestamp', True):
                p.setFont("Helvetica", 10)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                p.drawString(50, page_format[1] - 80, f"Generated: {timestamp}")
            
            # Add dashboard content (simplified)
            y_position = page_format[1] - 120
            p.setFont("Helvetica", 12)
            
            for widget in dashboard.widgets.all():
                if y_position < 100:  # Start new page if needed
                    p.showPage()
                    y_position = page_format[1] - 50
                
                p.drawString(50, y_position, f"Widget: {widget.widget_type}")
                y_position -= 20
                
                # Add widget configuration details
                p.setFont("Helvetica", 10)
                config_text = f"Configuration: {json.dumps(widget.configuration, indent=2)}"
                # Split long text into multiple lines
                lines = config_text.split('\n')
                for line in lines[:5]:  # Limit to 5 lines
                    if y_position < 50:
                        p.showPage()
                        y_position = page_format[1] - 50
                    p.drawString(70, y_position, line[:80])  # Limit line length
                    y_position -= 12
                
                y_position -= 20
                p.setFont("Helvetica", 12)
            
            p.save()
            return buffer.getvalue()
            
        except ImportError:
            # Fallback if reportlab is not available
            logger.warning("ReportLab not available, generating simple PDF")
            return self._generate_simple_pdf(dashboard, configuration)
    
    def _generate_simple_pdf(self, dashboard, configuration):
        """Generate a simple PDF without reportlab dependency."""
        # Create a simple HTML-to-PDF conversion or text-based PDF
        content = f"""
Dashboard Export: {dashboard.name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Widgets:
"""
        for widget in dashboard.widgets.all():
            content += f"- {widget.widget_type}: {widget.configuration.get('title', 'Untitled')}\n"
        
        # For now, return as bytes (in real implementation, use HTML-to-PDF library)
        return content.encode('utf-8')
    
    def _generate_png_export(self, dashboard, configuration):
        """Generate PNG export for dashboard."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Get resolution configuration
            resolution = configuration.get('resolution', '2x')
            scale_factor = {'1x': 1, '2x': 2, '3x': 3}.get(resolution, 2)
            
            # Base dimensions
            base_width = 1200
            base_height = 800
            
            # Create image with scaling
            width = base_width * scale_factor
            height = base_height * scale_factor
            
            # Create image
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to load a font
                font_title = ImageFont.truetype("arial.ttf", 24 * scale_factor)
                font_text = ImageFont.truetype("arial.ttf", 16 * scale_factor)
            except (OSError, IOError):
                # Fallback to default font
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
            
            # Add title if requested
            y_position = 20 * scale_factor
            if configuration.get('include_title', True):
                draw.text((20 * scale_factor, y_position), f"Dashboard: {dashboard.name}", 
                         fill='black', font=font_title)
                y_position += 40 * scale_factor
            
            # Add timestamp if requested
            if configuration.get('include_timestamp', True):
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                draw.text((20 * scale_factor, y_position), f"Generated: {timestamp}", 
                         fill='gray', font=font_text)
                y_position += 30 * scale_factor
            
            # Add widgets (simplified representation)
            widget_height = 100 * scale_factor
            widget_width = (width - 60 * scale_factor) // 2
            
            for i, widget in enumerate(dashboard.widgets.all()):
                if y_position + widget_height > height - 20 * scale_factor:
                    break  # Don't exceed image bounds
                
                x_position = 20 * scale_factor + (i % 2) * (widget_width + 20 * scale_factor)
                if i % 2 == 0 and i > 0:
                    y_position += widget_height + 20 * scale_factor
                
                # Draw widget box
                draw.rectangle([x_position, y_position, 
                              x_position + widget_width, y_position + widget_height], 
                              outline='black', fill='lightgray')
                
                # Add widget title
                widget_title = f"{widget.widget_type}: {widget.configuration.get('title', 'Untitled')}"
                draw.text((x_position + 10 * scale_factor, y_position + 10 * scale_factor), 
                         widget_title, fill='black', font=font_text)
            
            # Save to buffer
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', quality=95)
            return buffer.getvalue()
            
        except ImportError:
            # Fallback if PIL is not available
            logger.warning("PIL not available, generating placeholder PNG")
            return self._generate_placeholder_png(dashboard, configuration)
    
    def _generate_placeholder_png(self, dashboard, configuration):
        """Generate a placeholder PNG without PIL dependency."""
        # Create a minimal PNG (1x1 pixel) as placeholder
        # In real implementation, use a different image library or HTML-to-image service
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\xc1\x00\x00\x00\x00IEND\xaeB`\x82'
        return png_data


@shared_task
def process_dashboard_export(export_id):
    """Celery task to process dashboard exports."""
    try:
        export_job = DashboardExport.objects.get(id=export_id)
        export_job.status = 'processing'
        export_job.save(update_fields=['status'])
        
        handler = DashboardExportHandler()
        
        # Generate file based on format
        if export_job.export_format == 'csv':
            content = handler.process_csv_export(export_job.dashboard, export_job.configuration)
            file_extension = 'csv'
            content_type = 'text/csv'
        elif export_job.export_format == 'pdf':
            content = handler._generate_pdf_export(export_job.dashboard, export_job.configuration)
            file_extension = 'pdf'
            content_type = 'application/pdf'
        elif export_job.export_format == 'png':
            content = handler._generate_png_export(export_job.dashboard, export_job.configuration)
            file_extension = 'png'
            content_type = 'image/png'
        else:
            raise ValueError(f"Unsupported export format: {export_job.export_format}")
        
        # Save file
        filename = f"dashboard_{export_job.dashboard.id}_{export_job.id}.{file_extension}"
        file_path = f"dashboard_exports/{filename}"
        
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        default_storage.save(file_path, io.BytesIO(content))
        
        # Update export job
        export_job.file_path = file_path
        export_job.file_size = len(content)
        export_job.status = 'completed'
        export_job.completed_at = timezone.now()
        export_job.save(update_fields=['file_path', 'file_size', 'status', 'completed_at'])
        
        # Send email if requested
        if export_job.delivery_email:
            send_export_email.delay(str(export_job.id))
        
        logger.info(f"Dashboard export {export_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Dashboard export {export_id} failed: {str(e)}")
        
        try:
            export_job = DashboardExport.objects.get(id=export_id)
            export_job.status = 'failed'
            export_job.error_message = str(e)
            export_job.save(update_fields=['status', 'error_message'])
        except DashboardExport.DoesNotExist:
            pass


@shared_task
def send_export_email(export_id):
    """Send email notification for completed export."""
    try:
        export_job = DashboardExport.objects.get(id=export_id)
        
        if export_job.status == 'completed' and export_job.delivery_email:
            # This would integrate with your email system
            # For now, just log the action
            logger.info(f"Would send export email to {export_job.delivery_email} for export {export_id}")
            
    except DashboardExport.DoesNotExist:
        logger.error(f"Export job {export_id} not found for email delivery")


@shared_task
def process_scheduled_exports():
    """Process scheduled dashboard exports."""
    now = timezone.now()
    
    scheduled_exports = DashboardExport.objects.filter(
        is_scheduled=True,
        next_run__lte=now,
        status__in=['completed', 'failed']  # Only reschedule completed or failed jobs
    )
    
    for export_job in scheduled_exports:
        # Create a new export job based on the scheduled one
        new_export = DashboardExport.objects.create(
            dashboard=export_job.dashboard,
            requested_by=export_job.requested_by,
            export_format=export_job.export_format,
            configuration=export_job.configuration,
            delivery_email=export_job.delivery_email,
            is_scheduled=True,
            schedule_config=export_job.schedule_config
        )
        
        # Calculate next run time
        handler = DashboardExportHandler()
        new_export.next_run = handler._calculate_next_run(export_job.schedule_config)
        new_export.save(update_fields=['next_run'])
        
        # Update the original job's next run time
        export_job.next_run = new_export.next_run
        export_job.save(update_fields=['next_run'])
        
        # Queue the new export
        process_dashboard_export.delay(str(new_export.id))


# Singleton instance
dashboard_export_handler = DashboardExportHandler()