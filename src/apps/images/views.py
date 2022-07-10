from django.contrib.auth.models import User
from django.http import Http404

from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from src.apps.accounts.models import UserAccount
from src.apps.images.exceptions import InvalidImageAccessToken
from src.apps.images.models import Image, ImageAccessToken
from src.apps.images.permissions import (
    UserCanGenerateTemporaryLinkPermission,
    UserHasAccountPermission,
)
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


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    service_class = ImageService
    permission_classes = [UserHasAccountPermission]

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

    @swagger_auto_schema(request_body=ImageInputSerializer)
    def create(self, request, *args, **kwargs):
        serializer = ImageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_account = request.user.user_account
        image = self.service_class.upload_image(
            data=serializer.validated_data, user_account=user_account
        )
        return Response(
            self.get_serializer(image).data,
            status=status.HTTP_201_CREATED,
        )


class GenerateTemporaryLinkAPIView(generics.GenericAPIView):
    queryset = ImageAccessToken.objects.all()
    serializer_class = TemporaryLinkOutputSerializer
    permission_classes = [UserCanGenerateTemporaryLinkPermission]
    service_class = TemporaryLinkService

    @swagger_auto_schema(request_body=TemporaryLinkInputSerializer)
    def post(self, request, *args, **kwargs):

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
    queryset = ImageAccessToken.objects.all()
    serializer_class = TemporaryImageOutputSerializer
    service_class = TemporaryLinkService
    permission_classes = [permissions.AllowAny]

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
