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
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'sku', 'barcode', 'category', 'category_id', 'unit_price', 'weight', 'dimensions', 'variants']

    def validate_unit_price(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Unit price must be positive.")
        return value

    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("SKU must be unique.")
        return value

    def validate(self, data):
        # Example: Ensure category is present
        if not data.get('category'):
            raise serializers.ValidationError("Category is required.")
        return data
