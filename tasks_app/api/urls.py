from django.urls import path

from tasks_app.api.views import (
    AssignedToMeView,
    ReviewingView,
    TaskCommentDeleteView,
    TaskCommentListCreateView,
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks/<int:task_id>/", TaskRetrieveUpdateDestroyView.as_view(), name="task-detail"),
    path("tasks/assigned-to-me/", AssignedToMeView.as_view(), name="assigned-to-me"),
    path("tasks/reviewing/", ReviewingView.as_view(), name="reviewing"),
    path(
        "tasks/<int:task_id>/comments/",
        TaskCommentListCreateView.as_view(),
        name="task-comment-list-create",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        TaskCommentDeleteView.as_view(),
        name="task-comment-delete",
    ),
]