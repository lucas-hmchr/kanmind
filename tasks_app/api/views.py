from django.shortcuts import get_object_or_404

from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from tasks_app.api.permissions import (
    IsBoardMember,
    IsCommentAuthor,
    IsTaskCreatorOrBoardOwner,
)
from tasks_app.api.serializers import (
    CommentSerializer,
    TaskCreateUpdateSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
)
from tasks_app.models import Comment, Task


def raise_task_validation(message):
    raise ValidationError({"detail": message})


def _is_board_member(user, board):
        return user == board.owner or board.members.filter(id=user.id).exists()

class AssignedToMeView(generics.ListAPIView):
    """
    API view to list tasks assigned to the current user.
    """
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingView(generics.ListAPIView):
    """
    API view to list tasks where the current user is the reviewer.
    """
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)

class TaskListCreateView(generics.ListCreateAPIView):
    """
    API view to list and create tasks.
    List shows all tasks in boards where the user is a member.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user).distinct()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaskCreateUpdateSerializer
        return TaskListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = serializer.validated_data["board"]
        if not _is_board_member(request.user, board):
            self.permission_denied(
                request,
                message="You must be a board member to create a task.",
            )

        validate_board_users(board, serializer.validated_data)
        task = serializer.save(creator=request.user)

        output = TaskDetailSerializer(task)
        return Response(output.data, status=status.HTTP_201_CREATED)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific task.
    """
    queryset = Task.objects.all()
    lookup_url_kwarg = "task_id"

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsBoardMember()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskDetailSerializer
        return TaskCreateUpdateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        task = self.get_object()
        self.check_object_permissions(request, task)

        serializer = self.get_serializer(task, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if "board" in serializer.validated_data:
            return Response(
                {"detail": "Changing the board is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validate_board_users(task.board, serializer.validated_data)
        serializer.save()

        output = TaskDetailSerializer(task)
        return Response(output.data, status=status.HTTP_200_OK)


def validate_board_users(board, validated_data):
    assignee = validated_data.get("assignee")
    reviewer = validated_data.get("reviewer")

    if assignee and not _is_board_member(assignee, board):
        raise_task_validation("Assignee must be a board member.")

    if reviewer and not _is_board_member(reviewer, board):
        raise_task_validation("Reviewer must be a board member.")


class TaskCommentListCreateView(generics.ListCreateAPIView):
    """
    API view to list and create comments for a specific task.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "task_id"

    def get_task(self):
        return get_object_or_404(Task, pk=self.kwargs["task_id"])

    def get_queryset(self):
        task = self.get_task()
        if not _is_board_member(self.request.user, task.board):
            self.permission_denied(
                self.request,
                message="You must be a board member to access comments.",
            )
        return task.comments.all()

    def perform_create(self, serializer):
        task = self.get_task()
        if not _is_board_member(self.request.user, task.board):
            self.permission_denied(
                self.request,
                message="You must be a board member to comment on this task.",
            )
        serializer.save(author=self.request.user, task=task)


class TaskCommentDeleteView(generics.DestroyAPIView):
    """
    API view to delete a specific comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])
