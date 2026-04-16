from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from boards_app.models import Board
from tasks_app.models import Comment, Task

User = get_user_model()


class NotFoundPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Custom PrimaryKeyRelatedField that raises a 404 error if the object is not found.
    """
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=data)
        except queryset.model.DoesNotExist:
            raise NotFound("Board not found.")
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)

class TaskUserSerializer(serializers.ModelSerializer):
    """
    Compact serializer for user info in the context of tasks.
    """
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for task comments.
    """
    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]


class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing tasks with basic info.
    """
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single task.
    """
    board = serializers.IntegerField(source="board.id", read_only=True)
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating tasks.
    """
    board = NotFoundPrimaryKeyRelatedField(
        queryset=Board.objects.all(),
        required=False,
    )
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]