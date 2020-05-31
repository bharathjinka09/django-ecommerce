from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    # Leave as empty string for base url
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('logout_user/', views.logout_user, name="logout_user"),
    path('profile/', views.get_user_profile, name="profile"),

]
