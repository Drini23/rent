from django. urls import path
from . import views
from .views import reservation, calculate_total_cost

app_name = 'qera'

urlpatterns = [
    path('', views.home, name='home'),
    path('car_detail/<int:pk>/', views.car_detail, name='car_detail'),
    path('reserve/', views.reservation, name='reservation'),
    path('success/', views.success, name='success'),
    path('rezervime/', views.rezervime, name='reervime'),
    path('calculate_total_cost/', calculate_total_cost, name='calculate_total_cost'),
]