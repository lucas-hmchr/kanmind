from rest_framework.permissions import BasePermission


class IsBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = getattr(obj, "board", None)
        if board is None and hasattr(obj, "task"):
            board = obj.task.board

        if board is None:
            return False

        return request.user == board.owner or board.members.filter(
            id=request.user.id
        ).exists()


class IsTaskCreatorOrBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.creator or request.user == obj.board.owner


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author