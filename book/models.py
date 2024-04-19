from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=4,
        choices=CoverChoices,
        default=CoverChoices.HARD,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        decimal_places=2,
        max_digits=8,
    )

    class Meta:
        ordering = ("title", "author")
        verbose_name = "book"
        verbose_name_plural = "books"

    def __str__(self) -> str:
        return f"{self.title} - {self.author} (available: {self.inventory})"
