# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Cart, Order, Shipping, Payment, Product, Seller, UserProfile, Address
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserCreationForm, PaymentSlipForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ProductForm, UserProfileForm, AddressForm
from io import BytesIO
import base64
from .utils.promptpay import generate_promptpay_payload
from rest_framework import viewsets
from .serializers import ProductSerializer, OrderStatusSerializer
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import os



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



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



@login_required
def add_product_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)

            # ✅ ตรวจสอบว่า user มี Seller หรือยัง ถ้ายังให้สร้าง Seller ขึ้นมา
            try:
                seller = Seller.objects.get(user=request.user)
            except Seller.DoesNotExist:
                # ถ้าไม่มี Seller ให้สร้าง Seller ให้กับ User
                seller = Seller(user=request.user)
                seller.save()  # บันทึก Seller ใหม่ที่ผูกกับ User

            product.seller = seller  # กำหนดให้ product มี Seller ที่เพิ่งสร้างหรือมีอยู่แล้ว
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})
    
    
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

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'redirect_url': reverse('login')}, status=401)

    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

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



from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, Order, Shipping, Payment, Address

@login_required
@transaction.atomic
def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # ดึงที่อยู่ของ user จาก Address model
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')  # จาก dropdown เลือกที่อยู่
        full_name = request.POST.get('full_name', '').strip()
        address = request.POST.get('address', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        if selected_address_id:
            # กรณีเลือกที่อยู่จากโปรไฟล์
            selected_address = get_object_or_404(Address, pk=selected_address_id, user=request.user)
            full_name = f"{request.user.userprofile.first_name} {request.user.userprofile.last_name}"  # หรือจะเก็บใน Address ก็ได้
            address = f"{selected_address.address_line1} {selected_address.address_line2}, {selected_address.city}, {selected_address.state}, {selected_address.postal_code}, {selected_address.country}"
            phone_number = request.user.userprofile.phone_number
        else:
            # กรณีกรอกที่อยู่ใหม่ ต้องมั่นใจว่า full_name, address, phone_number ไม่ว่าง
            if not full_name or not address or not phone_number:
                # ส่ง error กลับไปยังฟอร์ม (ทำเพิ่มเองได้)
                context = {
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'addresses': addresses,
                    'error': 'กรุณากรอกข้อมูลที่อยู่ให้ครบ หรือเลือกที่อยู่จากรายการ',
                    'full_name': full_name,
                    'address': address,
                    'phone_number': phone_number,
                }
                return render(request, 'checkout.html', context)

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

        return redirect('payment_qr')  # ไปหน้า success หลังสั่งซื้อ

    # GET method
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'addresses': addresses,
    })


def order_success(request):
    # ดึงข้อมูลคำสั่งซื้อที่สำเร็จล่าสุดของผู้ใช้
    order = Order.objects.filter(user=request.user).latest('id')
    
    # ดึงข้อมูลการจัดส่งที่เชื่อมโยงกับคำสั่งซื้อ
    shipping_info = Shipping.objects.get(order=order)

    # ดึงข้อมูลตะกร้าจาก session
    cart_items_from_session = request.session.get('cart_data', [])

    # ส่งข้อมูลไปยัง template
    return render(request, 'order_success.html', {
        'shipping_info': shipping_info,
        'cart_items': cart_items_from_session,  # แสดงข้อมูลจาก session
        'total_price': order.total_price  # ใช้ราคาที่เก็บในคำสั่งซื้อ
    })

@login_required
def payment_qr_view(request):
    try:
        order = Order.objects.filter(user=request.user).latest('id')
        payment = Payment.objects.get(order=order)
        load_dotenv()
        promptpay_number = os.getenv("PROMPTPAY_NUMBER")
        amount = float(order.total_price)

        from promptpay import qrcode
        payload = qrcode.generate_payload(promptpay_number, amount=amount)
        qr = qrcode.to_image(payload)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        if request.method == 'POST':
            form = PaymentSlipForm(request.POST, request.FILES, instance=payment)
            if form.is_valid():
                payment.status = 'pending'  # ตั้งรอแอดมินตรวจสอบ
                form.save()
                # เพิ่ม message หรือ redirect ตามต้องการ
                return redirect('order_status')  # หรือ redirect กลับหน้าสแกน QR

        else:
            form = PaymentSlipForm(instance=payment)

        return render(request, 'payment_qr.html', {
            'order': order,
            'qr_base64': qr_base64,
            'amount': amount,
            'form': form,
            'payment_status': payment.status,
        })

    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

    


@login_required
def upload_payment_slip(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = get_object_or_404(Payment, order=order)

    if request.method == 'POST':
        form = PaymentSlipForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment.status = 'pending'  # ตั้งสถานะรอแอดมินตรวจสอบ
            form.save()
            return redirect('order_status')  # หรือหน้าแสดงสถานะคำสั่งซื้อ
    else:
        form = PaymentSlipForm(instance=payment)

    return render(request, 'upload_slip.html', {'form': form, 'order': order})

    

@login_required
def order_status_view(request):
    # ดึงคำสั่งซื้อทั้งหมดของผู้ใช้ โดยเรียงลำดับจากคำสั่งซื้อล่าสุด
    orders = Order.objects.filter(user=request.user).order_by('-id')

    # เตรียมข้อมูลรวมกับ shipping status
    order_status_list = []
    for order in orders:
        try:
            shipping = Shipping.objects.get(order=order)
        except Shipping.DoesNotExist:
            shipping = None

        order_status_list.append({
            'order': order,
            'shipping': shipping,
        })

    return render(request, 'order_status.html', {'order_status_list': order_status_list})


@login_required
@transaction.atomic
def order_delete_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # ตรวจสอบสถานะก่อนลบ (ตัวอย่างลบได้เฉพาะสถานะ 'Pending' เท่านั้น)
    if order.status.lower() != 'pending':
        messages.error(request, "ไม่สามารถลบคำสั่งซื้อที่ดำเนินการไปแล้วได้")
        return redirect('order_status')

    # ลบข้อมูลที่เกี่ยวข้องก่อน (ถ้ามี)
    order.delete()

    messages.success(request, f"ลบคำสั่งซื้อ #{order_id} สำเร็จ")
    return redirect('order_status')

def contact_view(request):
    return render(request, 'contact.html')



class LatestOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            order = Order.objects.filter(user=request.user).latest('id')
            serializer = OrderStatusSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'No order found.'}, status=status.HTTP_404_NOT_FOUND)
        


@login_required
def profile_view(request):
    # get or create profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    addresses = Address.objects.filter(user=request.user)

    return render(request, 'profile.html', {
        'form': form,
        'addresses': addresses,
    })

@login_required
def address_add(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('profile')
    else:
        form = AddressForm()
    return render(request, 'address_form.html', {'form': form})

@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'address_form.html', {'form': form})

@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('profile')
    return render(request, 'address_confirm_delete.html', {'address': address})