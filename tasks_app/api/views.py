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
    TaskSerializer,
)
from tasks_app.models import Comment, Task


def raise_task_validation(message):
    raise ValidationError({"detail": message})


class AssignedToMeView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user).distinct()

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return TaskCreateUpdateSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        if self.action in ["partial_update", "retrieve"]:
            return [IsAuthenticated(), IsBoardMember()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = serializer.validated_data["board"]
        if not self._is_board_member(request.user, board):
            self.permission_denied(
                request,
                message="You must be a board member to create a task.",
            )

        self._validate_board_users(board, serializer.validated_data)
        task = serializer.save(creator=request.user)
        output = TaskSerializer(task)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        self.check_object_permissions(request, task)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        self.check_object_permissions(request, task)

        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if "board" in serializer.validated_data:
            return Response(
                {"detail": "Changing the board is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self._validate_board_users(task.board, serializer.validated_data)
        task = serializer.save()
        output = TaskSerializer(task)
        return Response(output.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        self.check_object_permissions(request, task)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _is_board_member(self, user, board):
        return user == board.owner or board.members.filter(id=user.id).exists()

    def _validate_board_users(self, board, validated_data):
        assignee = validated_data.get("assignee")
        reviewer = validated_data.get("reviewer")

        if assignee and not self._is_board_member(assignee, board):
            raise_task_validation("Assignee must be a board member.")

        if reviewer and not self._is_board_member(reviewer, board):
            raise_task_validation("Reviewer must be a board member.")


class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_task(self):
        return get_object_or_404(Task, pk=self.kwargs["task_id"])

    def get_queryset(self):
        task = self.get_task()
        if not self._is_board_member(self.request.user, task.board):
            self.permission_denied(
                self.request,
                message="You must be a board member to access comments.",
            )
        return task.comments.all()

    def perform_create(self, serializer):
        task = self.get_task()
        if not self._is_board_member(self.request.user, task.board):
            self.permission_denied(
                self.request,
                message="You must be a board member to comment on this task.",
            )
        serializer.save(author=self.request.user, task=task)

    def _is_board_member(self, user, board):
        return user == board.owner or board.members.filter(id=user.id).exists()


class TaskCommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])