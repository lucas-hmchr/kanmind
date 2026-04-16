from django.db import models
from django.conf import settings

class Board(models.Model):
    """
    Represents a Kanban board.
    Boards have a title, an owner, and multiple members.
    """
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="boards",
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )
    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title