from django.urls import path, include
from . import views
from .views import ProductListView, ProductDetailView, cart_view, CustomLoginView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='sign_up'),
    path('auth/', include('social_django.urls', namespace='social')),
]