from django.db import models
# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

class Analytic(models.Model):
    report_name = models.CharField(max_length=255)
    data = models.JSONField()

class CarbonFootprint(models.Model):
    product = models.CharField(max_length=255)
    footprint = models.FloatField()

class Chat(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    
    # เลื่อนการนำเข้า Product ไปที่นี้
    def __init__(self, *args, **kwargs):
        from .models import Product  # เลื่อนการนำเข้าในตอนที่ต้องการใช้
        super().__init__(*args, **kwargs)
    
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity} pcs)"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

class Product(models.Model):
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)  # ความสัมพันธ์กับ Seller
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.CharField(max_length=100)
    eco_score = models.FloatField()
    image = models.ImageField(upload_to='product/', blank=True, null=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    from .models import Product
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # เชื่อมโยงกับ User
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # เชื่อมโยงกับ Product
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_product = models.CharField(max_length=255)

class Refund(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=50)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)

class Shipping(models.Model):
    STATUS_CHOICES = [
        ('pending', 'ยังไม่จัดส่ง'),
        ('shipped', 'ส่งพัสดุแล้ว'),
        ('in_transit', 'กำลังขนส่ง'),
        ('delivered', 'จัดส่งสำเร็จ'),
        ('failed', 'จัดส่งล้มเหลว'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, default='Unknown')
    address = models.TextField()
    phone_number = models.CharField(max_length=20, default='N/A')
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    shipping_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipping for Order {self.order.id} - Status: {self.shipping_status}"



class Support(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.TextField()
    status = models.CharField(max_length=50)