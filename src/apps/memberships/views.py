from rest_framework import viewsets
from src.apps.memberships.models import MembershipType
from src.apps.memberships.serializers import MembershipTypeOutputSerializer


class MembershipTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MembershipType.objects.all()
    serializer_class = MembershipTypeOutputSerializer
