from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  # หรือระบุ fields ที่ต้องการ เช่น ['id', 'name', 'price']
