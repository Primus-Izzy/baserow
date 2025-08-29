"""
URL patterns for batch record operations.
"""
from django.urls import path

from .views import BatchRecordOperationsView

app_name = "baserow.contrib.database.api.batch"

urlpatterns = [
    path(
        'records/',
        BatchRecordOperationsView.as_view(),
        name='batch_records'
    ),
]