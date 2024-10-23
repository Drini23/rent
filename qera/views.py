from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Payment
from django.http import JsonResponse
from datetime import datetime
from django.shortcuts import render, redirect
from .models import Car, Reservation
from .forms import ReservationForm


# Create your views here.


def home(request):
    cars = Car.objects.all()
    context = {'cars': cars, 'reservation': reservation}
    return render(request, 'qera/home.html', context)


def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    context = {'car': car}
    return render(request, 'qera/car_detail.html', context)


@login_required(login_url='signup')
# Reservation view for form submission
def reservation(request):
    cars = Car.objects.filter(availability_status=True)  # Only available cars

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)

            # Automatically set default status to 'PENDING'
            reservation.status = 'PENDING'

            # Calculate total cost
            pickup_date = form.cleaned_data['pickup_date']
            return_date = form.cleaned_data['return_date']
            car = form.cleaned_data['car']
            rental_days = (return_date - pickup_date).days

            # Calculate total cost and save it to the model instance
            reservation.total_cost = rental_days * car.rental_price

            # Save the reservation and redirect
            reservation.save()
            return redirect('qera:success')  # Update with actual success page URL

    else:
        form = ReservationForm()

    context = {
        'form': form,
        'cars': cars
    }

    return render(request, 'qera/reservation.html', context)


# View to calculate total cost (for AJAX request)
def calculate_total_cost(request):
    if request.method == "POST":
        try:
            # Retrieve form data from the request
            car_id = request.POST.get("car_id")
            pickup_date_str = request.POST.get("pickup_date")
            return_date_str = request.POST.get("return_date")

            # Fetch the car object
            car = Car.objects.get(id=car_id)

            # Convert string dates to datetime objects
            pickup_date = datetime.strptime(pickup_date_str, "%Y-%m-%dT%H:%M")
            return_date = datetime.strptime(return_date_str, "%Y-%m-%dT%H:%M")

            # Calculate the total rental days and total cost
            rental_days = (return_date - pickup_date).days
            total_cost = rental_days * car.rental_price

            # Return the total cost as JSON response
            return JsonResponse({"total_cost": total_cost}, status=200)
        except Exception as e:
            # Return an error response if something goes wrong
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required(login_url='signup')
def success(request):
    reservation = Reservation.objects.get(id=1)
    return render(request, 'qera/success.html', {'reservation': reservation})


@user_passes_test(lambda u: u.is_staff, login_url='qera:home')
def rezervime(request):
    rezervime = Reservation.objects.all()
    payment = Payment.objects.all()
    context = {'rezervime': rezervime, 'payment': payment}
    return render(request, 'qera/rezervime.html', context)
