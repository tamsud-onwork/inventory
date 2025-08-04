from rest_framework import serializers
from .models import Category, Product, ProductVariant

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True, required=False, allow_null=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True)
    variants = ProductVariantSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'sku', 'barcode', 'category', 'category_id', 'unit_price', 'weight', 'dimensions', 'variants']
        extra_kwargs = {
            'name': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'sku': {'required': False, 'allow_null': True},
            'barcode': {'required': False, 'allow_null': True},
            'unit_price': {'required': False, 'allow_null': True},
            'weight': {'required': False, 'allow_null': True},
            'dimensions': {'required': False, 'allow_null': True},
        }

    # All fields are now optional; remove required field validation
