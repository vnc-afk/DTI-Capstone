urlpatterns = [
    
]
# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("payment-page/", views.payment_page, name="payment-page"),
    path('gcash-payment/', views.gcash_payment, name='gcash_payment'),
    path('gcash_success/', views.gcash_success, name='gcash_success'),
]
