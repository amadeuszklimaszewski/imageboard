from rest_framework import viewsets
from rest_framework.response import Response

from src.apps.accounts.models import UserAccount
from src.apps.accounts.serializers import UserAccountOutputSerializer


class UserAccountViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = UserAccount.objects.all()
    serializer_class = UserAccountOutputSerializer

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(user=user)
