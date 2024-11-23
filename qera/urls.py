from django. urls import path
from . import views
from .views import reservation, calculate_total_cost, create_checkout_session, payment_page

app_name = 'qera'

urlpatterns = [
    path('', views.home, name='home'),
    path('car_detail/<int:car_id>/', views.car_detail, name='car_detail'),
    path('reserve/', views.reservation, name='reservation'),
    path('success/', views.success, name='success'),
    path('rezervime/', views.rezervime, name='reervime'),
    path('calculate_total_cost/', calculate_total_cost, name='calculate_total_cost'),
    path('create-checkout-session/<int:reservation_id>/', create_checkout_session, name='create_checkout_session'),
    path('payment/<int:reservation_id>/', payment_page, name='payment_page'),
    path('check_availability/', views.check_availability, name='check_availability'),
    path('about_us/', views.about_us, name='about_us')
]