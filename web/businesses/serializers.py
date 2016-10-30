from rest_framework import serializers

from web.businesses.models import Business


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('name', 'dispensary', 'delivery', 'certified_legal_compliance', 'created_date')