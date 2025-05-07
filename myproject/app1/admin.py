from django.contrib import admin
from .models import Product
from django.contrib.auth.models import User
# Register your models here.
from django.contrib import admin
from .models import *

models = [Admin, Analytic, CarbonFootprint, Cart, Chat, Order, Payment, Product,
          Recommendation, Refund, Review, Seller, Shipping, Support]

for model in models:
    admin.site.register(model)