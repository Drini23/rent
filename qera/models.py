from django.db import models
from django.contrib.auth.models import User


# Car Model
class Car(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    availability_status = models.BooleanField(default=True)  # True means available for rent
    image = models.ImageField(upload_to='cars/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.brand} ({self.year})"


class Customer(models.Model):

    name = models.CharField(max_length=250, default=None, null=True)
    last_name = models.CharField(max_length=250, default=None, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    license_number = models.CharField(max_length=20)

    def __str__(self):
        return self.address




# Reservation Model
from django.utils.timezone import now


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    name = models.CharField(max_length=250, null=True)
    last_name = models.CharField(max_length=250, null=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    pickup_date = models.DateTimeField()
    return_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate the number of rental days
        rental_days = (self.return_date - self.pickup_date).days

        if rental_days < 1:
            rental_days = 1  # Minimum of one day rental

        # Set the total cost based on the car's rental price and number of days
        self.total_cost = rental_days * self.car.rental_price

        # Call the parent class's save method
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.id} - {self.car.name} by {self.name}"


# Payment Model
class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Payment for Reservation {self.reservation.id} - {self.payment_status}"

