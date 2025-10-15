from django.urls import path
from . import views

urlpatterns = [
    path("payment-page/<str:document_type>/<int:document_id>/", views.payment_page, name="payment-page"),
    path('gcash_payment/', views.gcash_payment, name='gcash_payment'),
    path('gcash_success/', views.gcash_success, name='gcash_success'),
]
