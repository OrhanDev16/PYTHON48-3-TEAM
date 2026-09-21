from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=130, unigue=True)



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
