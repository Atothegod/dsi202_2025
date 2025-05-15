from django.urls import path, include
from . import views

from .views import ProductListView, ProductDetailView, cart_view, CustomLoginView,add_product_view, payment_qr_view, order_status_view, order_delete_view, contact_view, ProductViewSet

from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/add/', add_product_view, name='add_product'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('api/cart-count/', views.get_cart_count, name='get_cart_count'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='sign_up'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order_success/', views.order_success, name='order_success'),
    path('payment_qr/', payment_qr_view, name='payment_qr'),
    path('order_status/', order_status_view, name='order_status'),
    path('order_delete/<int:order_id>/', order_delete_view, name='order_delete'),
    path('contact/', views.contact_view, name='contact'),
    path('api/', include(router.urls)),
    
]