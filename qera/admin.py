from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Car)

admin.site.register(Payment)
admin.site.register(Reservation)
admin.site.register(CarImage)

from django.contrib import admin
from .models import Customer, Car, Reservation


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'last_name', 'phone', 'address', 'license_number')
    search_fields = ('user__username', 'name', 'last_name')  # Search by username or customer name
    list_filter = ('user',)

    def save_model(self, request, obj, form, change):
        # Automatically link the logged-in user as the customer
        if not obj.user:
            obj.user = request.user  # Set the user to the currently logged-in user if not set
        obj.save()

admin.site.register(Customer, CustomerAdmin)

