import os
import shutil
from datetime import timedelta
from django.test import override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from src.apps.accounts.models import UserAccount
from src.apps.images.models import (
    ImageAccessToken,
    Image as ImageModel,
    ThumbnailSize,
)
from src.apps.memberships.models import MembershipType
from tests.test_apps.test_images.utils import generate_image_file

User = get_user_model()

TEST_MEDIA_ROOT = "var/www/site/tmp/"


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestImageViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):

        cls.thumbnail_200px = ThumbnailSize.objects.create(height=200)
        cls.thumbnail_400px = ThumbnailSize.objects.create(height=400)

        cls.basic_membership = MembershipType.objects.create(
            name="Basic", contains_original_link=False, generates_expiring_link=False
        )
        cls.premium_membership = MembershipType.objects.create(
            name="Premium", contains_original_link=True, generates_expiring_link=False
        )
        cls.enterprise_membership = MembershipType.objects.create(
            name="Enterprise", contains_original_link=True, generates_expiring_link=True
        )

        cls.basic_membership.thumbnail_sizes.add(cls.thumbnail_200px)
        cls.premium_membership.thumbnail_sizes.add(
            cls.thumbnail_200px, cls.thumbnail_400px
        )
        cls.enterprise_membership.thumbnail_sizes.add(
            cls.thumbnail_200px, cls.thumbnail_400px
        )

        cls.user = User.objects.create(username="testuser")
        cls.user_account = UserAccount.objects.create(
            user=cls.user, membership_type=cls.enterprise_membership
        )
        cls.user_no_account = User.objects.create(username="invaliduser")

        file = generate_image_file()
        image_file = ContentFile(file.getvalue(), name=file.name)
        cls.img = ImageModel.objects.create(
            title="test", uploaded_by=cls.user_account, image=image_file
        )
        cls.post_image_data = {"image": file, "title": "test_tile"}

        cls.image_list_url = reverse("images:image-list")
        cls.image_detail_url = reverse("images:image-detail", kwargs={"pk": cls.img.pk})

    def setUp(self):
        self.client.force_login(user=self.user)

    def tearDown(self) -> None:
        for filename in os.listdir(TEST_MEDIA_ROOT):
            filepath = os.path.join(TEST_MEDIA_ROOT, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)
        return super().tearDown()

    def test_user_can_post_image(self):
        response = self.client.post(
            self.image_list_url, self.post_image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.data
        self.assertEqual(response_data["title"], self.post_image_data["title"])

    def test_user_without_account_cannot_post_image(self):
        self.client.force_login(user=self.user_no_account)
        response = self.client.post(
            self.image_list_url, self.post_image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_get_image_list(self):
        response = self.client.get(self.image_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data["results"]
        self.assertEqual(len(response_data), 1)

    def test_user_without_account_cannot_get_image_list(self):
        self.client.force_login(user=self.user_no_account)
        response = self.client.get(self.image_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_get_image_by_id(self):
        response = self.client.get(self.image_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_without_account_cannot_get_image_by_id(self):
        self.client.force_login(user=self.user_no_account)
        response = self.client.get(self.image_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymoususer_cannot_get_image_list(self):
        self.client.logout()
        response = self.client.get(self.image_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymoususer_cannot_get_image_by_id(self):
        self.client.logout()
        response = self.client.get(self.image_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basic_member_can_post_image(self):
        self.user_account.membership_type = self.basic_membership
        self.user_account.save()

        response = self.client.post(
            self.image_list_url, self.post_image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.data
        self.assertEqual(response_data["title"], self.post_image_data["title"])
        self.assertEqual(len(response_data["thumbnails"]), 1)

    def test_premium_member_can_post_image(self):
        self.user_account.membership_type = self.premium_membership
        self.user_account.save()

        response = self.client.post(
            self.image_list_url, self.post_image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.data
        self.assertEqual(response_data["title"], self.post_image_data["title"])
        self.assertEqual(len(response_data["thumbnails"]), 2)
        self.assertIn("image", response_data.keys())

    def test_enterprise_member_can_post_image(self):
        self.user_account.membership_type = self.enterprise_membership
        self.user_account.save()

        response = self.client.post(
            self.image_list_url, self.post_image_data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.data
        self.assertEqual(response_data["title"], self.post_image_data["title"])
        self.assertEqual(len(response_data["thumbnails"]), 2)
        self.assertIn("image", response_data.keys())
        self.assertIn("temporary_link_generator", response_data.keys())


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestTemporaryImageLinkViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.basic_membership = MembershipType.objects.create(
            name="Basic", contains_original_link=False, generates_expiring_link=False
        )
        cls.premium_membership = MembershipType.objects.create(
            name="Premium", contains_original_link=True, generates_expiring_link=False
        )
        cls.enterprise_membership = MembershipType.objects.create(
            name="Enterprise", contains_original_link=True, generates_expiring_link=True
        )

        cls.user = User.objects.create(username="testuser")
        cls.user_account = UserAccount.objects.create(
            user=cls.user, membership_type=cls.enterprise_membership
        )
        cls.user_no_account = User.objects.create(username="invaliduser")

        file = generate_image_file()
        image_file = ContentFile(file.getvalue(), name=file.name)
        cls.img = ImageModel.objects.create(
            title="test", uploaded_by=cls.user_account, image=image_file
        )

        cls.image_generate_link_url = reverse(
            "images:generate-image-link", kwargs={"pk": cls.img.pk}
        )
        cls.post_data = {"seconds": 4000}

        cls.access_token = ImageAccessToken.objects.create(
            image=cls.img, expires=timezone.now() + timedelta(seconds=30000)
        )
        cls.invalid_access_token = ImageAccessToken.objects.create(
            image=cls.img, expires=timezone.now() - timedelta(seconds=30000)
        )

        cls.temporary_link_url = reverse(
            "images:temporary-image", kwargs={"pk": cls.access_token.id}
        )
        cls.invalid_temporary_link_url = reverse(
            "images:temporary-image", kwargs={"pk": cls.invalid_access_token.id}
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def tearDown(self) -> None:
        for filename in os.listdir(TEST_MEDIA_ROOT):
            filepath = os.path.join(TEST_MEDIA_ROOT, filename)
            try:
                shutil.rmtree(filepath)
            except OSError:
                os.remove(filepath)
        return super().tearDown()

    def test_enterprise_member_can_post_temporary_image_link_generator(self):
        response = self.client.post(self.image_generate_link_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_without_account_cannot_post_temporary_image_link_generator(self):
        self.client.force_login(user=self.user_no_account)
        response = self.client.post(self.image_generate_link_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_basic_member_cannot_post_temporary_image_link_generator(self):
        self.user_account.membership_type = self.basic_membership
        self.user_account.save()

        response = self.client.post(self.image_generate_link_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_premium_member_cannot_post_temporary_image_link_generator(self):
        self.user_account.membership_type = self.premium_membership
        self.user_account.save()

        response = self.client.post(self.image_generate_link_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_get_image_by_temporary_link(self):
        response = self.client.get(self.temporary_link_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_with_no_account_can_get_image_by_temporary_link(self):
        self.client.force_login(self.user_no_account)
        response = self.client.get(self.temporary_link_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_can_get_image_by_temporary_link(self):
        self.client.logout()
        response = self.client.get(self.temporary_link_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_get_image_by_invalid_temporary_link(self):
        response = self.client.get(self.invalid_temporary_link_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
