from rest_framework import serializers
from .models import Supplier, SupplierProduct
from products.models import Product

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

    def validate_contact_email(self, value):
        if value and '@' not in value:
            raise serializers.ValidationError('Invalid email address.')
        return value

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Supplier name is required.')
        return value

class SupplierProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProduct
        fields = '__all__'
