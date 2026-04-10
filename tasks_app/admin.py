from django.contrib import admin

from tasks_app.models import Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board", "status", "priority", "due_date")
    search_fields = ("title", "description")
    list_filter = ("status", "priority", "due_date")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "author", "created_at")
    search_fields = ("content", "author__fullname", "task__title")