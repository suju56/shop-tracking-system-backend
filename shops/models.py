from django.db import models

# Create your models here.

class ShopCategory(models.Model):
    name = models.CharField(max_length = 300)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name 

class Shop(models.Model):
    name = models.CharField(max_length = 300)
    category = models.Foreignkey(ShopCategory, on_delete = models.CASCADE)
    address = models.TextField()
    description = models.TextField()
    email = models.EmailField(max_length = 300)
    phone_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 