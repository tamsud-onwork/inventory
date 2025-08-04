from django.db import models

# Create your models here.

class Stock(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey('warehouses.Location', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('product', 'location')

    def clean(self):
        if self.quantity < 0:
            from django.core.exceptions import ValidationError
            raise ValidationError({'quantity': 'Quantity cannot be negative.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class StockMovement(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True)
    movement_type = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    reference = models.CharField(max_length=100, null=True, blank=True)

class StockAdjustment(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True)
    ADJUSTMENT_TYPES = (
        ('ADD', 'Add'),
        ('REMOVE', 'Remove'),
        ('CORRECT', 'Correct'),
    )
    adjustment_type = models.CharField(max_length=50, choices=ADJUSTMENT_TYPES, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    approved_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
