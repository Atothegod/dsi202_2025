from django.contrib import admin
from .models import Product
from django.contrib.auth.models import User
# Register your models here.
from django.contrib import admin
from .models import *

# ลิสต์โมเดลที่ไม่รวม Shipping
models = [Admin, Analytic, CarbonFootprint, Cart, Chat, Order, Payment, Product,
          Recommendation, Refund, Review, Seller, Support]

for model in models:
    admin.site.register(model)

# ลงทะเบียน Shipping แบบมี custom admin
@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['order', 'shipping_status', 'tracking_number', 'last_updated']
    list_filter = ['shipping_status']
    search_fields = ['tracking_number', 'order__id']