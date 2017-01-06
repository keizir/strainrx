from rest_framework import permissions

from web.businesses.models import Business


class BusinessAccountOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            # Allow any GET request but restrict all others (POST, PUT, DELETE)
            return True

        business_id = view.kwargs.get('business_id')
        filterargs = {'users__id': request.user.id, 'pk': business_id}
        return Business.objects.filter(**filterargs).exists()
