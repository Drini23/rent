from django import forms
from .models import Car, Reservation, User

class ReservationForm(forms.ModelForm):
    pickup_date = forms.DateTimeField(
        widget=forms.TextInput(attrs={'type': 'datetime-local', 'readonly': True}),
        label="Pickup Date"
    )
    return_date = forms.DateTimeField(
        widget=forms.TextInput(attrs={'type': 'datetime-local', 'readonly': True}),
        label="Return Date"
    )
    name = forms.CharField(max_length=100, label="Full Name")
    last_name = forms.CharField(max_length=100, label="Last Name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=15, label="Phone Number")

    class Meta:
        model = Reservation
        fields = ['name', 'last_name', 'email', 'phone', 'car', 'pickup_date', 'return_date', 'user']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        car = kwargs.pop('car', None)
        initial_data = kwargs.get('initial', {})
        email = kwargs.pop('email', None)
        super().__init__(*args, **kwargs)

        # Pre-fill the user's information if available
        if user:
            self.fields['user'].queryset = User.objects.filter(id=user.id)
            self.fields['user'].initial = user
            self.fields['user'].widget.attrs['readonly'] = True
            self.fields['email'].initial = user.email
            self.fields['email'].widget.attrs['readonly'] = True

        # Pre-fill the car field if provided
        if car:
            self.fields['car'].queryset = Car.objects.filter(id=car.id)
            self.fields['car'].initial = car
            self.fields['car'].widget.attrs['readonly'] = True

        # Pre-fill pickup_date and return_date from initial_data
        if 'pickup_date' in initial_data:
            self.fields['pickup_date'].initial = initial_data['pickup_date']
            self.fields['pickup_date'].widget.attrs['readonly'] = True

        if 'return_date' in initial_data:
            self.fields['return_date'].initial = initial_data['return_date']
            self.fields['return_date'].widget.attrs['readonly'] = True

