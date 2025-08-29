from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CollaborationViewSet

app_name = "baserow.contrib.database.api.collaboration"

router = DefaultRouter()
router.register("collaboration", CollaborationViewSet, basename="collaboration")

urlpatterns = [
    path("", include(router.urls)),
]