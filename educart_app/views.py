from django.shortcuts import render,redirect,get_object_or_404
from .models import EmailConfirmation,State, City, Category, Subcategory
import random
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, AddressForm
from django.utils import timezone
from .models import OTPToken,Logo,Profile,Address
from django.contrib.auth import login,logout, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from Educart.backends import EmailBackend
from django.contrib.auth.decorators import login_required
import secrets


User = get_user_model()


def validate_email(request):
    email = request.GET.get('email', None)
    data = {
        'exists': User.objects.filter(email=email).exists()
    }
    return JsonResponse(data)

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'exists': User.objects.filter(username=username).exists()
    }
    return JsonResponse(data)

def email_confirmation_view(request):
    logo = Logo.objects.all()
    return render(request,'educart_app/email_confirmation.html',{'logo':logo})


def email_confirmation(request, token):
    email_confirmation = get_object_or_404(EmailConfirmation, token=token)
    user = email_confirmation.user
    user.is_active = True
    user.save()
    email_confirmation.delete()
    messages.success(request, 'Thanks for verifying your account. Now you can login.')
    # Render the email confirmation template
    return render(request, 'educart_app/email_confirmation.html')

def generate_unique_token():
    token = secrets.token_urlsafe(32)
    return token

def send_email_confirmation(user,request):
    token = generate_unique_token()  # Replace with your token generation logic
    email_confirmation = EmailConfirmation.objects.create(user=user, token=token)
    to_email = [user.email]
    subject = 'Email Confirmation'
    message = f'Click the following link to confirm your email: {request.build_absolute_uri("/email-confirmation/" + token + "/")}'
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, to_email)
    email.content_subtype = 'html'
    email.send()


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Check if a Profile instance already exists for the user
            profile, created = Profile.objects.get_or_create(user=user)

            # Update the phone number
            phone_number = form.cleaned_data.get('phone_number')
            profile.phone_number = phone_number
            profile.save()

            send_email_confirmation(user, request)
            messages.success(request, 'We have sent you a account confirmation email to your entered account. Please confirm your account via this given link')
            return redirect('/')
        else:
            errors = form.errors
            for field, error in errors.items():
                for e in error:
                    messages.error(request, f"{e}")
            return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'educart_app/signup.html', {'form': form})

def generate_otp():
    digits = "0123456789"
    return ''.join(random.choice(digits) for _ in range(6))

def create_otp(user):
    otp_token = OTPToken.objects.create(user=user, token=generate_otp())
    return otp_token

def send_otp_email(request):
    # Generate OTP
    if request.method =='POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)            
        except User.DoesNotExist:
            response_data = {'success': False,'message':"user with this email doesn't exists!"}
            return JsonResponse(response_data) 

        otp = create_otp(user)
        # Compose the email subject and message
        subject = 'Educart OTP verification'
        to_email = [email]
        logo = Logo.objects.all()
        # Render the HTML template with the context data
        html_content = render_to_string('educart_app/otp_email_template.html', {'otp': otp,'for':'login','logo':logo})

        email = EmailMessage(subject, html_content, settings.EMAIL_HOST_USER, to_email)
        email.content_subtype = 'html'
        email.send()
        response_data = {'success': True,'message':"OTP sent successfully!!"}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'response':'error while sending the OTP'})


def verify_otp(user, otp):
    otp_token = OTPToken.objects.filter(user=user, token=otp).order_by('-created_at').last()
    if otp_token:
        time_difference = timezone.now() - otp_token.created_at
        if time_difference.seconds < 300:  # OTP expires after 5 minutes (300 seconds)
            otp_token.delete()
            return True
    return False


from django.contrib.auth import authenticate, login
from django.http import JsonResponse

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        otp = request.POST.get('otp')
        user = None

        if password != 'None':
            # Authenticating user with email and password
            user = EmailBackend.authenticate(request, email, password, None)
        elif otp != 'None':
            # Authenticating user with email and OTP
            user = EmailBackend.authenticate(request, email, None, otp=otp)
            if user and verify_otp(user, otp):
                request.session['authenticated'] = True
                OTPToken.objects.all().delete()

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'You have been logged in successfully!!')
                return JsonResponse({'success': True, 'response': 'Logged in successfully!'})
            else:
                return JsonResponse({'success': False, 'response': 'This account is inactive. Activate your account by clicking on the confirmation link that we have sent to your e-mail'})
        else:
            return JsonResponse({'success': False, 'response': 'Please enter correct credentials!'})
    return redirect('/')

def logout_view(request):
    logout(request)
    # Perform any additional actions or redirect to a desired page
    # For example, you can redirect to the homepage:
    messages.success(request, "You have been logged out sucessfully!!")
    return redirect('/')

@login_required(login_url='/')
def change_password(request):
    if request.method == 'POST':
        form_data = PasswordChangeForm(request.user, request.POST)
        if form_data.is_valid():
            print(form_data.is_valid())
            form_data.save()
            return JsonResponse({'success': True})
        else:
        # Return a success response
            return JsonResponse({'success': False, 'error':'Please! Check your credential carefully!!'})
    
    else:
        form  = PasswordChangeForm(request.user)
        return render(request, 'educart_app/change-password.html', {'form':form})

# ###################################################################


# functions to render the templates

def dashboard(request):
    category = Category.objects.all()
    return render(request, 'educart_app/dashboard.html',{'category':category})

def product_detail(request):
    return render(request, 'educart_app/productdetail.html')

@login_required(login_url='/')
def shopping_cart(request):
    return render(request, 'educart_app/shoppingcart.html')

@login_required(login_url='/')
def checkout(request):
    return render(request, 'educart_app/checkout.html')

@login_required(login_url='/')
def user_account(request):
    return render(request, 'educart_app/user-account.html')

@login_required(login_url='/')
def user_profile(request):
    profile = request.user.profile
    address = Address.objects.filter(profile=profile)[:2]
    return render(request, 'educart_app/user-profile.html',{'address':address})

@login_required(login_url='/')
def your_orders(request):
    return render(request,'educart_app/your_orders.html')

def search_products(request):
    search_query = request.GET.get('query')
    # products = Product.objects.filter(name__icontains=search_query)
    return render(request, 'educart_app/productlist.html', {'search_query': search_query})

@login_required(login_url='/')
def my_wishlist(request):
    return render(request, 'educart_app/my-wishlist.html')

@login_required(login_url='/')
def manage_address(request):
    profile = request.user.profile
    address = Address.objects.filter(profile=profile)
    if request.method == 'POST':
        form = AddressForm(request.user, request.POST)
        if form.is_valid():               
            address = form.save(commit=False)
            address.profile = profile
            address.save()
            return JsonResponse({'success': True, 'message': "Address has been saved successfully!"})
        else:
            return JsonResponse({'success': False, 'message': 'Error while saving the address. Try again later'})
    
    else:
        form = AddressForm(request.user)
        return render(request, 'educart_app/manage-address.html', {'form': form, 'addresses': address})


def user_login(request):
    return render(request, 'educart_app/login.html')


def delete_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('id')
        try:
            address = Address.objects.get(id=address_id)  # Retrieve the address object
            address.delete()  # Delete the address
            return JsonResponse({'success': True, 'message':'Address has been deleted successfully!!'})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Address not found'})
    
    # If the request method is not POST, return an error response
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def update_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('id')
        try:
            address = Address.objects.get(id=address_id)
            form = AddressForm(request.user, request.POST, instance=address)
            print(address)
            print(form.is_valid())
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True, 'message': 'Address has been updated successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid form data'})
            
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Address not found'})

    # If the request method is not POST, return an error response
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def get_cities(request):
    state = request.GET.get('state')
    cities = City.objects.filter(state=state).values('id', 'name')
    return JsonResponse(list(cities), safe=False)

def get_state(request):
    state = State.objects.all().values('id', 'name')
    return JsonResponse(list(state), safe=False)