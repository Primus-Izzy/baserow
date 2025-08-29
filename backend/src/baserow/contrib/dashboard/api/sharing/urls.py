from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardSharingViewSet, public_dashboard_view, embed_dashboard_view, embed_widget_view

router = DefaultRouter()
router.register(r'dashboards', DashboardSharingViewSet, basename='dashboard-sharing')

urlpatterns = [
    path('', include(router.urls)),
    path('public/<str:token>/', public_dashboard_view, name='public-dashboard'),
    path('embed/<str:token>/', embed_dashboard_view, name='embed-dashboard'),
    path('embed/widget/<str:token>/', embed_widget_view, name='embed-widget'),
]