from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from src.apps.images.models import Image
from src.apps.images.serializers import (
    BasicImageOutputSerializer,
    EnterpriseImageOutputSerializer,
    ImageInputSerializer,
    ImageOutputSerializer,
    PremiumImageOutputSerializer,
)
from src.apps.images.services import ImageService


class ImageViewSet(CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageOutputSerializer
    serializer_classes = {
        "Enterprise": EnterpriseImageOutputSerializer,
        "Premium": PremiumImageOutputSerializer,
        "Basic": BasicImageOutputSerializer,
    }
    service_class = ImageService

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % self.__class__.__name__
        )
        account = self.request.user.user_account
        return self.serializer_classes.get(
            account.membership_type.name, self.serializer_classes["Basic"]
        )

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(uploaded_by__user=user)

    def create(self, request, *args, **kwargs):
        serializer = ImageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = self.service_class.upload_image(
            data=serializer.validated_data, request_user=request.user
        )
        return Response(
            self.get_serializer(image).data,
            status=status.HTTP_201_CREATED,
        )
