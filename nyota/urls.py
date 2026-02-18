from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('offer-selection/', views.offer_selection, name='offer_selection'),
    path('payment-status/', views.payment_status, name='payment_status'),
    path('api/payment-status/<str:reference>/', views.check_payment_status_api, name='check_payment_status_api'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('api/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
]
