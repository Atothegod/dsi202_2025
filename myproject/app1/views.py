# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Cart, Order, Shipping, Payment, Product
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def homepage_view(request):
    return render(request, 'homepage.html')

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = super().get_queryset()  # Get the default queryset (all bikes)
        query = self.request.GET.get('q')  # Get the search term from the URL (e.g., ?q=mountain)
        if query:
            # Filter bikes where name or description contains the query (case-insensitive)
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    
    
@login_required
def cart_view(request):
    carts = Cart.objects.filter(user=request.user)
    total_price = sum(cart_item.product.price * cart_item.quantity for cart_item in carts)
    return render(request, 'cart.html', {'carts': carts, 'total_price': total_price})


@login_required
def get_cart_count(request):
    """
    API endpoint สำหรับดึงข้อมูลจำนวนสินค้าในตะกร้า
    """
    # นับจำนวนสินค้าทั้งหมดในตะกร้า (รวมปริมาณของแต่ละรายการ)
    cart_items = Cart.objects.filter(user=request.user)
    total_items = sum(item.quantity for item in cart_items)
    
    return JsonResponse({'cart_count': total_items})

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        # เช็คว่าในตะกร้ามีสินค้านี้อยู่หรือไม่ ถ้ามีเพิ่มจำนวน ถ้าไม่มีก็เพิ่มใหม่
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        cart_items = Cart.objects.filter(user=request.user)
        total_items = sum(item.quantity for item in cart_items)
        return JsonResponse({'total_items': total_items})

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_view')



class CustomLoginView(LoginView):
    template_name = 'login.html'
    
    

    def form_valid(self, form):
        user = form.get_user()  # Get the logged-in user
        login(self.request, user)  # Log the user in
        
        # Get 'next' URL from POST data or fallback to home
        next_url = self.request.POST.get('next', '/')
        print(f"Redirecting to: {next_url}")  # Print next URL to check in the console

        return redirect(next_url)
    
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # หรือเปลี่ยนเส้นทางที่ต้องการ
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
@transaction.atomic
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        full_name = request.POST['full_name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']

        # 1. สร้างคำสั่งซื้อ
        order = Order.objects.create(
            user=request.user,
            status='Pending',
            total_price=total_price
        )

        # 2. เพิ่มที่อยู่จัดส่ง
        Shipping.objects.create(
            order=order,
            full_name=full_name,
            address=address,
            phone_number=phone_number
        )

        # 3. เพิ่มการชำระเงินแบบ mock (คุณสามารถเปลี่ยนเป็นระบบจริงได้ภายหลัง)
        Payment.objects.create(
            order=order,
            method='COD',  # Cash on Delivery
            status='Pending'
        )

        # 4. ล้างตะกร้า
        cart_items.delete()

        return redirect('order_success')  # ไปหน้า success หลังสั่งซื้อ

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })
    
def order_success(request):
    return render(request, 'order_success.html')