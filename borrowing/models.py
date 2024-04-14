from django.contrib.auth import get_user_model
from django.db.models import Q, F
from django.db.models.constraints import CheckConstraint
from django.db import models

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(
        null=True,
        blank=True,
        default=None,
    )
    book = models.ForeignKey(
        Book,
        related_name="borrowings",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        get_user_model(),
        related_name="borrowings",
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("borrow_date", "expected_return_date",)
        constraints = [
            CheckConstraint(
                check=(
                        Q(borrow_date__lt=F("expected_return_date"))
                        & Q(borrow_date__lt=F("actual_return_date"))
                ),
                name="borrow_date_lt_expected_and_actual_return_date",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} borrows '{self.book.title}'"
