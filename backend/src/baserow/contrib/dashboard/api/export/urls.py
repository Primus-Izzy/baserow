from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardExportViewSet

router = DefaultRouter()
router.register(r'dashboards', DashboardExportViewSet, basename='dashboard-export')

urlpatterns = [
    path('', include(router.urls)),
]