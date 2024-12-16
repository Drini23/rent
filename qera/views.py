import stripe
import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ReservationForm
from .models import Payment
from django.shortcuts import render
from django.db.models import Q
from .models import Car, Reservation
from .utils import send_payment_email
from django.utils.dateparse import parse_datetime

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY_TEST_MODE
stripe.publice_key = settings.STRIPE_PUBLIC_KEY


def home(request):
    pickup_date = request.GET.get('pickup_date')
    return_date = request.GET.get('return_date')

    if pickup_date and return_date:
        from datetime import datetime
        pickup_date = datetime.strptime(pickup_date, "%Y-%m-%d").date()
        return_date = datetime.strptime(return_date, "%Y-%m-%d").date()

        reserved_cars = Reservation.objects.filter(
            Q(pickup_date__lte=return_date, return_date__gte=pickup_date)
        ).values_list('car_id', flat=True)

        cars = Car.objects.exclude(id__in=reserved_cars)
    else:
        cars = Car.objects.all()

    return render(request, 'qera/home.html', {'cars': cars})


def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    pickup_date = request.GET.get('pickup_date', '')
    return_date = request.GET.get('return_date', '')

    context = {
        'car': car,
        'pickup_date': pickup_date,
        'return_date': return_date,
    }
    return render(request, 'qera/car_detail.html', context)


@login_required(login_url='signup')
def reservation(request):
    # Get query parameters from the URL
    car_id = request.GET.get('car_id')
    pickup_date = request.GET.get('pickup_date')
    return_date = request.GET.get('return_date')

    # Convert the date strings into a proper datetime format
    if pickup_date:
        pickup_date = parse_datetime(pickup_date)  # This converts string to datetime
    if return_date:
        return_date = parse_datetime(return_date)

    # Get the car instance or return a 404 if not found
    car = get_object_or_404(Car, id=car_id) if car_id else None

    # Prepare initial data for the form
    initial_data = {}
    if pickup_date:
        initial_data['pickup_date'] = pickup_date
    if return_date:
        initial_data['return_date'] = return_date

    if request.method == 'POST':
        form = ReservationForm(request.POST, user=request.user, car=car, initial=initial_data)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.car = car
            reservation.status = 'PENDING'

            # Calculate total cost
            pickup_date = form.cleaned_data['pickup_date']
            return_date = form.cleaned_data['return_date']
            rental_days = (return_date - pickup_date).days
            reservation.total_cost = rental_days * car.winter_rental_price

            reservation.save()
            return redirect('qera:payment_page', reservation_id=reservation.id)
    else:
        form = ReservationForm(user=request.user, car=car, initial=initial_data)

    context = {
        'form': form,
        'car': car,  # Pass car data to the template if needed
    }
    return render(request, 'qera/reservation.html', context)


def calculate_total_cost(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        car_id = data.get('car_id')
        pickup_date = data.get('pickup_date')
        return_date = data.get('return_date')
    elif request.method == 'GET':
        # Get data from query parameters for GET requests
        car_id = request.GET.get('car_id')
        pickup_date = request.GET.get('pickup_date')
        return_date = request.GET.get('return_date')

    if not car_id or not pickup_date or not return_date:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    # Calculate the number of days between pickup and return
    pickup_date = datetime.strptime(pickup_date, '%Y-%m-%d')
    return_date = datetime.strptime(return_date, '%Y-%m-%d')
    days_rented = (return_date - pickup_date).days

    if days_rented <= 0:
        return JsonResponse({'error': 'Invalid rental period'}, status=400)

    # Example: Assume the car has a fixed daily rate
    daily_rate = 50  # Replace with actual rate logic
    total_cost = daily_rate * days_rented

    return JsonResponse({'total_cost': total_cost})


@login_required(login_url='signup')
def success(request):
    reservation = Reservation.objects.filter().last()

    if reservation and not reservation.email_sent:
        # Send email to user
        user_email = request.user.email
        username = request.user.get_full_name() or request.user.username
        amount = reservation.total_cost

        email_sent = send_payment_email(user_email, username, amount, reservation.id, reservation.car)

        if email_sent:
            # Mark the email as sent
            reservation.email_sent = True
            reservation.save()
            print(f"Email successfully sent to {user_email}")
        else:
            print(f"Failed to send email to {user_email}")
    else:
        if reservation:
            print("Email already sent for this reservation.")

    return render(request, 'qera/success.html', {'reservation': reservation})


@user_passes_test(lambda u: u.is_staff, login_url='qera:home')
def rezervime(request):
    rezervime = Reservation.objects.all()
    payment = Payment.objects.all()
    context = {'rezervime': rezervime, 'payment': payment}
    return render(request, 'qera/rezervime.html', context)


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
                    'unit_amount': int(reservation.total_cost * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
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


@csrf_exempt
def check_availability(request):
    if request.method == "POST":
        try:
            # Parse incoming data
            data = json.loads(request.body)
            car_id = data.get("car_id")
            pickup_date = parse_date(data.get("pickup_date"))
            return_date = parse_date(data.get("return_date"))

            # Debug logs
            print(f"Received data: car_id={car_id}, pickup_date={pickup_date}, return_date={return_date}")

            # Validate data
            if not (car_id and pickup_date and return_date):
                print("Invalid input data")
                return JsonResponse({"error": "Invalid input"}, status=400)

            # Convert both input and reservation dates to `datetime.date`
            pickup_date = pickup_date.date() if isinstance(pickup_date, datetime) else pickup_date
            return_date = return_date.date() if isinstance(return_date, datetime) else return_date

            # Fetch the car
            car = Car.objects.get(id=car_id)
            print(f"Car fetched: {car}")

            # Fetch reservations for the car
            reservations = Reservation.objects.filter(car=car)
            print(f"Reservations for car: {reservations}")

            # Check availability
            for reservation in reservations:
                res_pickup = reservation.pickup_date.date() if isinstance(reservation.pickup_date,
                                                                          datetime) else reservation.pickup_date
                res_return = reservation.return_date.date() if isinstance(reservation.return_date,
                                                                          datetime) else reservation.return_date

                print(f"Checking reservation: {reservation}")
                print(f"Reservation period: {res_pickup} to {res_return}")

                # Compare dates
                if not (return_date <= res_pickup or pickup_date >= res_return):
                    print("Car is not available during this period")
                    return JsonResponse({"is_available": False})

            print("Car is available")
            return JsonResponse({"is_available": True})

        except Car.DoesNotExist:
            print("Car does not exist")
            return JsonResponse({"error": "Car not found"}, status=404)
        except Exception as e:
            print(f"Error occurred: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)


def about_us(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            # Example: Sending an email to site admin
            send_mail(
                subject=f"Contact Form Submission from {name}",
                message=message,
                from_email=email,
                recipient_list=[settings.DEFAULT_CONTACT_EMAIL],  # Add your admin email
            )
            messages.success(request, "Your message has been sent successfully!")
        else:
            messages.error(request, "Please fill out all fields.")

    return render(request, 'qera/about_us.html')
