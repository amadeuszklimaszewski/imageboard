from django.contrib import admin

from src.apps.images.models import Image, ImageAccessToken, Thumbnail, ThumbnailSize


admin.site.register(Image)
admin.site.register(ThumbnailSize)
admin.site.register(Thumbnail)
admin.site.register(ImageAccessToken)
