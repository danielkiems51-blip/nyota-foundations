from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('api/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
]
