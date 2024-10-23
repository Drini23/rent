from django import forms
from .models import Car, Reservation

class ReservationForm(forms.ModelForm):
    pickup_date = forms.DateTimeField(
        widget=forms.TextInput(attrs={'type': 'datetime-local'}),
        label="Pickup Date"
    )
    return_date = forms.DateTimeField(
        widget=forms.TextInput(attrs={'type': 'datetime-local'}),
        label="Return Date"
    )
    name = forms.CharField(max_length=100, label="Full Name")
    last_name = forms.CharField(max_length=100, label="Last Name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=15, label="Phone Number")

    class Meta:
        model = Reservation
        # Remove 'total_cost' from fields
        fields = ['name', 'last_name', 'email', 'phone', 'car', 'pickup_date', 'return_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'car': forms.Select(attrs={'class': 'form-control'}),
            'pickup_date': forms.TextInput(attrs={'class': 'form-control'}),
            'return_date': forms.TextInput(attrs={'class': 'form-control'}),
        }
