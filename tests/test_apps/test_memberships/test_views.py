from django.urls import reverse

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from src.apps.accounts.models import UserAccount
from src.apps.images.models import ThumbnailSize
from src.apps.memberships.models import MembershipType

User = get_user_model()


class TestMembershipTypeViewset(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.user_account = UserAccount.objects.create(
            user=cls.user,
        )
        cls.thumbnail_size = ThumbnailSize.objects.create(height=500)
        cls.membership_type = MembershipType.objects.create(
            name="test", contains_original_link=False, generates_expiring_link=False
        )
        cls.membership_type.thumbnail_sizes.add(cls.thumbnail_size)

        cls.membership_type_list_url = reverse("memberships:membership-list")
        cls.membership_type_detail_url = reverse(
            "memberships:membership-detail",
            kwargs={"pk": cls.membership_type.id},
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_membership_type_list(self):
        response = self.client.get(self.membership_type_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        membership_type_data = response.data["results"][0]

        self.assertEqual(membership_type_data["name"], self.membership_type.name)

    def test_user_can_retrieve_membership_type_by_id(self):
        response = self.client.get(self.membership_type_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        membership_type_data = response.data

        self.assertEqual(membership_type_data["name"], self.membership_type.name)

    def test_anonymous_user_cannot_retrieve_membership_type_list(self):
        self.client.logout()
        response = self.client.get(self.membership_type_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_retrieve_membership_type_list(self):
        self.client.logout()
        response = self.client.get(self.membership_type_detail_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
