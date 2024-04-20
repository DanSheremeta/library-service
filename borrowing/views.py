from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer, BorrowingCreateSerializer, BorrowingReturnSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Borrowing.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "borrowing_return":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def get_queryset(self):
        """Retrieve the borrowings with filters"""
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if self.request.user.is_staff and user_id:
            queryset = queryset.filter(user__id=int(user_id))

        if is_active:
            queryset = queryset.filter(is_active=is_active)

        return queryset

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        book.inventory -= 1
        book.save()
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def borrowing_return(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(
            borrowing,
            data={
                "user": borrowing.user.id,
                "is_active": borrowing.is_active
            },
            context={"request": self.request}
        )

        serializer.is_valid(raise_exception=True)
        book = borrowing.book
        book.inventory += 1
        book.save()
        serializer.save(is_active=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="Filter by user id (available only for admins)",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by is_active (True/False)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List user's borrowings with filter by user_id(for admin) or is_active"""
        return super().list(request, *args, **kwargs)
