from django.db import models

# Create your models here.

class PurchaseOrder(models.Model):
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.PROTECT)
    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50)
    order_date = models.DateTimeField(auto_now_add=True)
    expected_date = models.DateTimeField(null=True, blank=True)

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class SalesOrder(models.Model):
    customer = models.ForeignKey('users.Customer', on_delete=models.PROTECT)
    created_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50)
    order_date = models.DateTimeField(auto_now_add=True)
    shipped_date = models.DateTimeField(null=True, blank=True)

class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
