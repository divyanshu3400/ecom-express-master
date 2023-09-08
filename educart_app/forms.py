from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from.models import Address

class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat password'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        errors = {}

        # Check if username or email already exists
        
        if User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists.'
            
        if User.objects.filter(email=email).exists():
            errors['email'] = 'Email address already exists.'

        # Check if password1 and password2 match
        if password1 and password2 and password1 != password2:
            errors['password2'] = 'Passwords do not match.'
            
        if errors:
            raise ValidationError(errors)
        
        # Save the hashed password to the user object
        self.instance.password = make_password(password1)
        
        return cleaned_data
    
    
class AddressForm(forms.ModelForm):
    def __init__(self, user, *args, state_choices=None, **kwargs):
        self.user = user
        self.state_choices = state_choices
        super(AddressForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Address
        exclude = ['profile', 'latitude', 'longitude']
        widgets = {
            'address_line_1': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'country': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        }
    
    
    def clean(self):
        cleaned_data = super().clean()
        address_line_1 = cleaned_data.get('address_line_1')
        city = cleaned_data.get('city')
        state = cleaned_data.get('state')
        postal_code = cleaned_data.get('postal_code')
        country = cleaned_data.get('country')
        
        if not address_line_1 or not city or not state or not postal_code or not country:
            raise forms.ValidationError("Please fill in all required fields.")
        
        return cleaned_data
