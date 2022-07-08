from django.contrib.auth.models import User
from django.http import Http404

from rest_framework import viewsets, status, generics
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from src.apps.accounts.models import UserAccount
from src.apps.images.exceptions import InvalidImageAccessToken
from src.apps.images.models import Image
from src.apps.images.serializers import (
    ImageInputSerializer,
    BasicImageOutputSerializer,
    OriginalImageOutputSerializer,
    ImageWithLinkOutputSerializer,
    OriginalImageWithLinkOutputSerializer,
    TemporaryImageOutputSerializer,
    TemporaryLinkInputSerializer,
    TemporaryLinkOutputSerializer,
)
from src.apps.images.services import ImageService, TemporaryLinkService


class ImageViewSet(CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    service_class = ImageService

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(uploaded_by__user=user)

    def get_serializer_class(self):
        account = self.request.user.user_account
        membership = account.membership_type
        if not membership:
            return BasicImageOutputSerializer

        if membership.contains_original_link and membership.generates_expiring_link:
            return OriginalImageWithLinkOutputSerializer

        if membership.contains_original_link:
            return OriginalImageOutputSerializer

        if membership.generates_expiring_link:
            return ImageWithLinkOutputSerializer

        return BasicImageOutputSerializer

    def _validate_user_account(self, request_user: User) -> UserAccount:
        account = request_user.user_account
        if account is None:
            raise PermissionDenied(
                "Invalid request user. User account does not exist in the database."
            )
        return account

    def create(self, request, *args, **kwargs):
        serializer = ImageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user_account = self._validate_user_account(request.user)
            image = self.service_class.upload_image(
                data=serializer.validated_data, user_account=user_account
            )
            return Response(
                self.get_serializer(image).data,
                status=status.HTTP_201_CREATED,
            )
        except PermissionDenied as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)


class GenerateTemporaryLinkAPIView(generics.CreateAPIView):
    serializer_class = TemporaryLinkOutputSerializer
    service_class = TemporaryLinkService

    def _validate_user_account(self, request_user: User) -> UserAccount:
        account = request_user.user_account
        if account is None or account.membership_type.generates_expiring_link is False:
            raise Http404

    def create(self, request, *args, **kwargs):
        self._validate_user_account(request_user=request.user)

        image_id = kwargs.get("pk")
        serializer = TemporaryLinkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = self.service_class.create_access_token(
            image_id=image_id, data=serializer.validated_data
        )
        return Response(
            self.get_serializer(access_token).data,
            status=status.HTTP_201_CREATED,
        )


class TemporaryImageLinkAPIView(generics.RetrieveAPIView):
    serializer_class = TemporaryImageOutputSerializer
    service_class = TemporaryLinkService

    def get(self, request, *args, **kwargs):
        access_token_id = kwargs.get("pk")
        try:
            image = self.service_class.get_image_from_token(
                access_token_id=access_token_id
            )
            return Response(
                self.get_serializer(image).data,
                status=status.HTTP_200_OK,
            )
        except InvalidImageAccessToken as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)
