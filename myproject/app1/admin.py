from django.contrib import admin
from .models import Product
from django.contrib.auth.models import User
# Register your models here.
from django.contrib import admin
from .models import *

# ลิสต์โมเดลที่ไม่รวม Shipping
models = [Admin, Analytic, CarbonFootprint, Cart, Chat, Order, Product,
          Recommendation, Refund, Review, Seller, Support]

for model in models:
    admin.site.register(model)

# ลงทะเบียน Shipping แบบมี custom admin
@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['order', 'shipping_status', 'tracking_number', 'last_updated']
    list_filter = ['shipping_status']
    search_fields = ['tracking_number', 'order__id']
    

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'get_user', 'status', 'slip_image', 'updated_at']
    list_filter = ['status']
    search_fields = ['order__id', 'order__user__username']
    readonly_fields = ['slip_image_preview']

    def get_user(self, obj):
        return obj.order.user
    get_user.short_description = 'User'
    get_user.admin_order_field = 'order__user'  # ทำให้ sort ได้ใน admin

    def slip_image_preview(self, obj):
        if obj.slip_image:
            return f'<img src="{obj.slip_image.url}" width="200" />'
        return "No slip uploaded"
    slip_image_preview.allow_tags = True
    slip_image_preview.short_description = "Slip Preview"