from django.urls import reverse

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from src.apps.accounts.models import UserAccount

User = get_user_model()


class TestUserAccountViewset(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.user_account = UserAccount.objects.create(
            user=cls.user,
        )
        cls.other_user = User.objects.create(username="otheruser")
        cls.other_user_account = UserAccount.objects.create(
            user=cls.other_user,
        )
        cls.admin = User.objects.create(username="admin", is_superuser=True)
        cls.admin_account = UserAccount.objects.create(
            user=cls.admin,
        )

        cls.user_account_list_url = reverse("accounts:user-list")
        cls.user_account_detail_url = reverse(
            "accounts:user-detail",
            kwargs={"pk": cls.user_account.id},
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_account_list(self):
        response = self.client.get(self.user_account_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        user_account_data = response.data["results"][0]
        user_data = user_account_data["user"]

        self.assertEqual(user_data["username"], self.user.username)
        self.assertEqual(user_data["email"], self.user.email)

    def test_user_can_retrieve_account_by_id(self):
        response = self.client.get(self.user_account_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_account_data = response.data
        user_data = user_account_data["user"]

        self.assertEqual(user_data["username"], self.user.username)
        self.assertEqual(user_data["email"], self.user.email)

    def test_other_user_cannot_retrieve_other_users_account(self):
        self.client.force_login(user=self.other_user)
        response = self.client.get(self.user_account_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_user_cannot_retrieve_account_list(self):
        self.client.logout()
        response = self.client.get(self.user_account_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_user_can_retrieve_users_account_list(self):
        self.client.force_login(user=self.admin)
        response = self.client.get(self.user_account_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_admin_user_can_retrieve_other_users_account(self):
        self.client.force_login(user=self.admin)
        response = self.client.get(self.user_account_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_account_data = response.data
        user_data = user_account_data["user"]

        self.assertEqual(user_data["username"], self.user.username)
        self.assertEqual(user_data["email"], self.user.email)
