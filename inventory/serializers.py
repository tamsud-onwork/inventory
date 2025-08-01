from rest_framework import serializers
from .models import Stock, StockMovement, StockAdjustment

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError('Quantity cannot be negative.')
        return value

    def validate(self, data):
        product = data.get('product')
        location = data.get('location')
        if product and location:
            if Stock.objects.filter(product=product, location=location).exists():
                raise serializers.ValidationError('Stock for this product/location already exists.')
        return data

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = '__all__'

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be positive.')
        return value

    def validate_movement_type(self, value):
        valid_types = dict(StockMovement.MOVEMENT_TYPES)
        if value not in valid_types:
            raise serializers.ValidationError('Invalid movement type.')
        return value

class StockAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustment
        fields = '__all__'

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be positive.')
        return value

    def validate_adjustment_type(self, value):
        valid_types = dict(StockAdjustment.ADJUSTMENT_TYPES)
        if value not in valid_types:
            raise serializers.ValidationError('Invalid adjustment type.')
        return value

    def validate(self, data):
        # Example business rule: Only admin/manager can approve
        approved_by = data.get('approved_by')
        if approved_by and hasattr(approved_by, 'role'):
            if approved_by.role not in ['admin', 'manager']:
                raise serializers.ValidationError('Only admin or manager can approve stock adjustments.')
        return data
