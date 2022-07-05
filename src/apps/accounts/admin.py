from django.contrib import admin

from src.apps.accounts.models import UserAccount

admin.site.register(UserAccount)
