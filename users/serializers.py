from rest_framework import serializers
from .models import Employee, Customer
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    class Meta:
        model = Employee
        fields = ['id', 'user', 'user_id', 'name', 'role']

    def validate_role(self, value):
        valid_roles = ['admin', 'manager', 'employee']
        if value not in valid_roles:
            raise serializers.ValidationError('Invalid role.')
        return value

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Employee name is required.')
        return value

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user', 'user_id', 'name', 'contact_email', 'contact_phone', 'address']

    def validate_contact_email(self, value):
        if value and '@' not in value:
            raise serializers.ValidationError('Invalid email address.')
        return value

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Customer name is required.')
        return value
