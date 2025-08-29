from django.urls import include, path

from .data_sources import urls as data_source_urls
from .widgets import urls as widget_urls
from .widgets import enhanced_urls as enhanced_widget_urls
from .sharing import urls as sharing_urls
from .export import urls as export_urls

app_name = "baserow.contrib.dashboard.api"


urlpatterns = [
    path("", include(widget_urls, namespace="widgets")),
    path("", include(data_source_urls, namespace="data_sources")),
    path("enhanced/", include(enhanced_widget_urls, namespace="enhanced_widgets")),
    path("sharing/", include(sharing_urls, namespace="sharing")),
    path("exports/", include(export_urls, namespace="exports")),
]
