from rest_framework import serializers
from .models import Warehouse, Location

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

    def validate_capacity(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('Capacity must be positive.')
        return value

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
