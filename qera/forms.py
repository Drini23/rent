from django import forms
from .models import Car, Reservation, User

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
        fields = ['name', 'last_name', 'email', 'phone', 'car', 'pickup_date', 'return_date', 'user']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'car': forms.Select(attrs={'class': 'form-control'}),
            'pickup_date': forms.TextInput(attrs={'class': 'form-control'}),
            'return_date': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve the user from kwargs
        super().__init__(*args, **kwargs)

        # Set the user field to display the logged-in user's name only
        if user:
            self.fields['user'].queryset = User.objects.filter(id=user.id)  # Restrict to the logged-in user
            self.fields['user'].initial = user  # Set initial value to the logged-in user
            self.fields['user'].empty_label = None  # Remove the empty option (---)
            self.fields['user'].widget.attrs['readonly'] = True  # Make it read-only
