from django.contrib import admin
from .models import Product

# Register your models here.
from django.contrib import admin
from .models import *

models = [Admin, Analytic, CarbonFootprint, Cart, Chat, Order, Payment, Product,
          Recommendation, Refund, Review, Seller, Shipping, Support, User]

for model in models:
    admin.site.register(model)