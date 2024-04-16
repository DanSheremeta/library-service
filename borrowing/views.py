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

        if borrowing.user != self.request.user:
            return Response(
                {"error": "You can not return someone else's borrowing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not borrowing.is_active:
            return Response(
                {"error": "You can not return inactive borrowing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = borrowing.book
        book.inventory += 1
        book.save()

        borrowing.is_active = False
        borrowing.save()
        message = {
            "message": f"You successfully returned {book.title} book!"
        }

        return Response(message, status=status.HTTP_201_CREATED)
