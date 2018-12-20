from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from web.businesses.api.permissions import BusinessLocationAccountOwnerOrStaff
from web.businesses.api.serializers import BusinessLocationGrownStrainItemSerializer
from web.businesses.models import BusinessLocation, BusinessLocationGrownStrainItem


class GrownStrainViewSet(ModelViewSet):
    permission_classes = (BusinessLocationAccountOwnerOrStaff,)
    serializer_class = BusinessLocationGrownStrainItemSerializer
    http_method_names = ('get', 'post', 'delete')

    def dispatch(self, request, *args, **kwargs):
        self.location = get_object_or_404(BusinessLocation, pk=kwargs['business_location_id'], grow_house=True)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return BusinessLocationGrownStrainItem.objects \
            .filter(business_location__id=self.kwargs['business_location_id']) \
            .order_by('strain__name')
