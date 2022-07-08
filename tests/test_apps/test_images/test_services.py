from datetime import timedelta
from django import test
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from src.apps.accounts.models import UserAccount
from src.apps.images.exceptions import InvalidImageAccessToken
from src.apps.images.models import (
    ImageAccessToken,
    Image as ImageModel,
    Thumbnail,
    ThumbnailSize,
)
from src.apps.memberships.models import MembershipType
from src.apps.images.services import ImageService, TemporaryLinkService
from tests.test_apps.test_images.utils import generate_image_file

User = get_user_model()


class TestImageService(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_class = ImageService

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

        cls.image_file = generate_image_file()
        cls.image = ContentFile(cls.image_file.getvalue(), name=cls.image_file.name)
        cls.image_data = {"title": "test", "image": cls.image}

    def test_image_service_correctly_uploads_image(self):
        image_instance = self.service_class.upload_image(
            data=self.image_data, user_account=self.user_account
        )
        self.assertEqual(image_instance.uploaded_by, self.user_account)
        self.assertEqual(image_instance.title, self.image_data["title"])

        result = ImageModel.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], image_instance)

    def test_image_service_correctly_creates_enterprise_thumbnails(self):
        image = ImageModel.objects.create(
            title="test", uploaded_by=self.user_account, image=self.image
        )
        self.service_class.create_thumbnails(
            image_model=image,
            thumbnail_sizes=self.enterprise_membership.thumbnail_sizes.all(),
        )
        result = Thumbnail.objects.all()
        self.assertEqual(len(result), 2)

    def test_image_service_correctly_creates_premium_thumbnails(self):
        image = ImageModel.objects.create(
            title="test", uploaded_by=self.user_account, image=self.image
        )
        self.service_class.create_thumbnails(
            image_model=image,
            thumbnail_sizes=self.premium_membership.thumbnail_sizes.all(),
        )
        result = Thumbnail.objects.all()
        self.assertEqual(len(result), 2)

    def test_image_service_correctly_creates_basic_thumbnail(self):
        image = ImageModel.objects.create(
            title="test", uploaded_by=self.user_account, image=self.image
        )
        self.service_class.create_thumbnails(
            image_model=image,
            thumbnail_sizes=self.basic_membership.thumbnail_sizes.all(),
        )
        result = Thumbnail.objects.all()
        self.assertEqual(len(result), 1)


class TestTemporaryLinkService(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_class = TemporaryLinkService

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

        cls.image_file = generate_image_file()
        cls.image = ContentFile(cls.image_file.getvalue(), name=cls.image_file.name)
        cls.image_model = ImageModel.objects.create(
            title="test", uploaded_by=cls.user_account, image=cls.image
        )
        cls.link_data = {"seconds": 3000}

    def test_temporary_link_service_correctly_creates_access_token(self):
        token = self.service_class.create_access_token(
            image_id=self.image_model.id, data=self.link_data
        )
        self.assertEqual(token.image, self.image_model)
        result = ImageAccessToken.objects.all()
        self.assertEqual(len(result), 1)

    def test_get_image_from_token(self):
        expire_date = timezone.now() + timedelta(seconds=4000)
        access_token = ImageAccessToken.objects.create(
            image=self.image_model, expires=expire_date
        )

        image = self.service_class.get_image_from_token(access_token_id=access_token.id)
        self.assertEqual(image, self.image_model)

    def test_get_image_from_token_raises_invalid_image_access_token_exception(self):
        invalid_expire_date = timezone.now() - timedelta(seconds=4000)
        invalid_access_token = ImageAccessToken.objects.create(
            image=self.image_model, expires=invalid_expire_date
        )
        with self.assertRaises(InvalidImageAccessToken):
            image = self.service_class.get_image_from_token(
                access_token_id=invalid_access_token.id
            )
        result = ImageAccessToken.objects.all()
        self.assertEqual(len(result), 0)
