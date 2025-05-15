# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Payment, UserProfile, Address


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'eco_score', 'image']  # ใส่ 'stock' ให้ครบ
        
        
class PaymentSlipForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['slip_image']
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone_number']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['label', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']