from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.api.permissions import IsBoardMemberOrOwner, IsBoardOwner
from boards_app.api.serializers import (
    BoardCreateUpdateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    UserSummarySerializer,
)
from boards_app.models import Board

User = get_user_model()


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing boards.
    Supports list, create, retrieve, partial_update, and destroy actions.
    """
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()

    def get_queryset(self):
        if self.action == "list":
            user = self.request.user
            return Board.objects.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()
        return Board.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BoardListSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        return BoardCreateUpdateSerializer

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)
        self._set_members(board, serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = BoardListSerializer(serializer.instance)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        board = self.get_object()
        self.check_object_permissions(request, board)
        serializer = BoardDetailSerializer(board)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        board = self.get_object()
        self.check_object_permissions(request, board)
        serializer = self.get_serializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self._set_members(board, serializer.validated_data)
        return Response(self._build_update_response(board))

    def destroy(self, request, *args, **kwargs):
        board = self.get_object()
        IsBoardOwner().has_object_permission(request, self, board) or self.permission_denied(
            request, message="Only the owner can delete this board."
        )
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ["list", "create"]:
            return [IsAuthenticated()]
        if self.action in ["retrieve", "partial_update"]:
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated()]

    def _set_members(self, board, validated_data):
        if "members" not in validated_data:
            return
        members = validated_data["members"]
        board.members.set(members)
        board.members.add(board.owner)

    def _build_update_response(self, board):
        return {
            "id": board.id,
            "title": board.title,
            "owner_data": UserSummarySerializer(board.owner).data,
            "members_data": UserSummarySerializer(board.members.all(), many=True).data,
        }


class EmailCheckView(APIView):
    """
    API view to check if a user with a specific email exists.
    Returns user summary if found.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Email query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSummarySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)