from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Car)
admin.site.register(Customer)
admin.site.register(Payment)
admin.site.register(Reservation)