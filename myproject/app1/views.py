# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Product, Cart
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView


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
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        return redirect('cart_view')

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
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # หรือเปลี่ยนเส้นทางที่ต้องการ
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})