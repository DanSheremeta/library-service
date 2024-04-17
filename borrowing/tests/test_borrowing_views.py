import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingListSerializer, BorrowingCreateSerializer

BORROWING_URL = reverse("borrowing:borrowing-list")

def sample_book(**params) -> Book:
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "inventory": 10,
        "daily_fee": 5.5,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)

def sample_borrowing(user, **params) -> Borrowing:
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    defaults = {
        "expected_return_date": tomorrow,
        "book": sample_book(),
        "user": user,
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.admin = get_user_model().objects.create_superuser(
            "admin@test.com",
            "testpass",
        )
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_borrowing_create(self):
        book = sample_book()
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        payload = {
            "expected_return_date": tomorrow,
            "book": book.id,
        }

        res = self.client.post(BORROWING_URL, payload)

        borrowing = Borrowing.objects.get(id=1)
        book_udt = Book.objects.get(id=book.id)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["book"], borrowing.book.id)
        self.assertEqual(res.data["expected_return_date"], str(borrowing.expected_return_date))
        self.assertEqual(book_udt.inventory, book.inventory - 1)
        self.assertEqual(borrowing.user, self.user)

        # Test create when book inventory is 0
        book.inventory = 0
        book.save()

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_borrowing_list(self):
        # Test list for admin user
        borrowing1 = sample_borrowing(self.user)
        borrowing2 = sample_borrowing(self.admin)

        self.client.force_authenticate(self.admin)
        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        ser1 = BorrowingListSerializer(borrowings, many=True)
        ser2 = BorrowingListSerializer(borrowing2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser1.data)
        self.assertIn(ser2.data, res.data)

        # Test list for default user
        self.client.force_authenticate(self.user)
        res = self.client.get(BORROWING_URL)

        ser = BorrowingListSerializer(borrowing1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ser.data, res.data)
        self.assertNotIn(ser2.data, res.data)

    def test_borrowing_list_filter_by_user_id(self):
        # Test list for default user
        borrowing1 = sample_borrowing(self.user)
        borrowing2 = sample_borrowing(self.admin)

        res = self.client.get(BORROWING_URL, {"user_id": self.admin.id})

        ser1 = BorrowingListSerializer(borrowing1)
        ser2 = BorrowingListSerializer(borrowing2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ser1.data, res.data)
        self.assertNotIn(ser2.data, res.data)

        # Test for admin user
        self.client.force_authenticate(self.admin)
        res1 = self.client.get(BORROWING_URL, {"user_id": self.user.id})
        res2 = self.client.get(BORROWING_URL, {"user_id": self.admin.id})

        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertIn(ser1.data, res1.data)
        self.assertNotIn(ser2.data, res1.data)

        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIn(ser2.data, res2.data)
        self.assertNotIn(ser1.data, res2.data)

    def test_borrowing_list_filter_by_is_active(self):
        borrowing1 = sample_borrowing(self.user)
        borrowing2 = sample_borrowing(self.admin)

        res1 = self.client.get(BORROWING_URL, {"is_active": True})
        res2 = self.client.get(BORROWING_URL, {"is_active": False})

        ser1 = BorrowingListSerializer(borrowing1)
        ser2 = BorrowingListSerializer(borrowing2)

        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIn(ser1.data, res1.data)
        self.assertNotIn(ser2.data, res1.data)
        self.assertNotIn(ser1.data, res2.data)
        self.assertNotIn(ser2.data, res2.data)

    def test_borrowing_return(self):
        borrowing = sample_borrowing(self.user)
        book_inventory = borrowing.book.inventory

        url = reverse("borrowing:borrowing-returning", args=[borrowing.id])
        res = self.client.post(url)

        borrowing_updt = Borrowing.objects.get(id=borrowing.id)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book_inventory + 1, borrowing_updt.book.inventory)
        self.assertNotEqual(borrowing.is_active, borrowing_updt.is_active)

    def test_borrowing_invalid_return(self):
        borrowing = sample_borrowing(self.user)
        url = reverse("borrowing:borrowing-returning", args=[borrowing.id])

        # Inactive borrowing
        borrowing.is_active = False
        borrowing.save()
        res1 = self.client.post(url)
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid user
        self.client.force_authenticate(self.admin)
        res2 = self.client.post(url)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
