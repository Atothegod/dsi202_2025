from django.urls import path
from . import views
from .views import ProductListView, ProductDetailView


urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]