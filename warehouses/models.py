from django.db import models

# Create your models here.

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    capacity = models.IntegerField()

class Location(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, blank=True)
