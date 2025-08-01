from rest_framework import serializers
from .models import PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'supplier', 'created_by', 'status', 'order_date', 'expected_date', 'items']

    def validate_status(self, value):
        valid_status = ['open', 'received', 'cancelled']
        if value not in valid_status:
            raise serializers.ValidationError('Invalid status.')
        return value

    def validate(self, data):
        if not data.get('supplier'):
            raise serializers.ValidationError('Supplier is required.')
        return data

class SalesOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = '__all__'

class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = SalesOrder
        fields = ['id', 'customer', 'created_by', 'status', 'order_date', 'shipped_date', 'items']

    def validate_status(self, value):
        valid_status = ['open', 'shipped', 'cancelled']
        if value not in valid_status:
            raise serializers.ValidationError('Invalid status.')
        return value

    def validate(self, data):
        if not data.get('customer'):
            raise serializers.ValidationError('Customer is required.')
        return data
