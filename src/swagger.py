from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="imageboard", default_version="v1", description="Image uploading API"
    ),
    public=False,
    permission_classes=(AllowAny,),
)
