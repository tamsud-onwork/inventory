from django.db import models

# Create your models here.

class Stock(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    location = models.ForeignKey('warehouses.Location', on_delete=models.CASCADE)
    quantity = models.IntegerField()

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
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=50)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, blank=True)

class StockAdjustment(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    ADJUSTMENT_TYPES = (
        ('ADD', 'Add'),
        ('REMOVE', 'Remove'),
        ('CORRECT', 'Correct'),
    )
    adjustment_type = models.CharField(max_length=50, choices=ADJUSTMENT_TYPES)
    quantity = models.IntegerField()

    def clean(self):
        if self.quantity < 0:
            from django.core.exceptions import ValidationError
            raise ValidationError({'quantity': 'Quantity cannot be negative.'})
        if self.adjustment_type not in dict(self.ADJUSTMENT_TYPES):
            from django.core.exceptions import ValidationError
            raise ValidationError({'adjustment_type': 'Invalid adjustment type.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey('users.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
