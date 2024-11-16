import stripe
from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from datetime import datetime
from .models import Car, Reservation, Customer
from .forms import ReservationForm
from .models import Payment


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
def reservation(request):
    cars = Car.objects.filter(availability_status=True)  # Only available cars

    if request.method == 'POST':
        form = ReservationForm(request.POST, user=request.user)  # Pass the user to the form
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user  # Set the user on the reservation
            reservation.status = 'PENDING'

            # Calculate total cost
            pickup_date = form.cleaned_data['pickup_date']
            return_date = form.cleaned_data['return_date']
            car = form.cleaned_data['car']
            rental_days = (return_date - pickup_date).days

            reservation.total_cost = rental_days * car.rental_price
            reservation.save()
            return redirect('qera:payment_page', reservation_id=reservation.id)

    else:
        form = ReservationForm(user=request.user)  # Pass the user to the form

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
    reservation = Reservation.objects.filter().last()
    return render(request, 'qera/success.html', {'reservation': reservation})


@user_passes_test(lambda u: u.is_staff, login_url='qera:home')
def rezervime(request):
    rezervime = Reservation.objects.all()
    payment = Payment.objects.all()
    context = {'rezervime': rezervime, 'payment': payment}
    return render(request, 'qera/rezervime.html', context)


stripe.api_key = settings.STRIPE_SECRET_KEY_TEST_MODE
stripe.publice_key = settings.STRIPE_PUBLIC_KEY


@csrf_exempt
def create_checkout_session(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Reservation {reservation.id} for {reservation.car}',
                    },
                    'unit_amount': int(reservation.total_cost * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/success/',
        )

        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@login_required(login_url='signup')
def payment_page(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    context = {
        'reservation': reservation,

        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'qera/payment_page.html', context)
