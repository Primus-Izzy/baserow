from django.urls import path

from .views import KanbanViewView, KanbanViewMoveCardView, KanbanViewColumnsView

app_name = "baserow.contrib.database.api.views.kanban"

urlpatterns = [
    path("<int:view_id>/", KanbanViewView.as_view(), name="list"),
    path("<int:view_id>/move-card/", KanbanViewMoveCardView.as_view(), name="move_card"),
    path("<int:view_id>/columns/", KanbanViewColumnsView.as_view(), name="columns"),
]