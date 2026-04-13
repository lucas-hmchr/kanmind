from django.urls import path
from rest_framework.routers import DefaultRouter

from tasks_app.api.views import (
    AssignedToMeView,
    ReviewingView,
    TaskCommentDeleteView,
    TaskCommentListCreateView,
    TaskViewSet,
)

router = DefaultRouter(trailing_slash=True)
router.register("tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    path("tasks/assigned-to-me/", AssignedToMeView.as_view(), name="assigned-to-me"),
    path("tasks/reviewing/", ReviewingView.as_view(), name="reviewing"),
    path(
        "tasks/<int:task_id>/comments/",
        TaskCommentListCreateView.as_view(),
        name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        TaskCommentDeleteView.as_view(),
        name="task-comment-delete",
    ),
]

urlpatterns += router.urls