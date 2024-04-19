from rest_framework import serializers

from book.models import Book
from borrowing.models import Borrowing
from book.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError("There is no available book to borrow")
        return book


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "is_active",
        )

    def validate_user(self, user):
        if user != self.context["request"].user:
            raise serializers.ValidationError("You can not return someone else's borrowing")
        return user

    def validate_is_active(self, is_active):
        print("validate is_active called")
        if not is_active:
            raise serializers.ValidationError("You can not return inactive borrowing")
        return is_active
