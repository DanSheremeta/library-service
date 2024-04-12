from rest_framework.viewsets import ModelViewSet

from book.models import Book
from book.serializers import BookSerializer
from book.permissions import IsAdminUserOrReadOnly


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
