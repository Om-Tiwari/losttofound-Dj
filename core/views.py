from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .views import *
from .forms import *
from .models import *
import boto3
import uuid
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class S3Storage(S3Boto3Storage):
    location ='img/people/'


def upload_image_to_s3(image_file):
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_S3_REGION_NAME)

    s3_storage = S3Storage()

    # Generate a unique filename for the image
    filename = str(uuid.uuid4())

    # Upload the image to S3
    s3_storage.save(filename, image_file)

    # Return the URL of the uploaded image
    return s3_storage.url(filename)


@login_required(login_url='signin')
def index(request):
    people = Person.objects.all()
    form = PersonForm()
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            image_url = upload_image_to_s3(image_file)
            person = Person(
                name=form.cleaned_data['name'],
                age=form.cleaned_data['age'],
                gender=form.cleaned_data['gender'],
                last_seen=form.cleaned_data['last_seen'],
                contact_info=form.cleaned_data['contact_info'],
                description=form.cleaned_data['description'],
                image=image_url,
            )
            person.save()
            messages.success(request, 'Complained Filed Successfully')

    context = {
        'form': form,
        'people': people,
        'title': "Index",
    }
    return render(request, 'index.html', context=context)


def home(request):
    if request.user.is_authenticated:
        return redirect('index')
    context = {
        'title': "Home"
    }
    return render(request, 'home.html', context)


def signin(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Loged In")
            return redirect('index')
        else:
            messages.error(request, 'Username or Password is incorrect')
    context = {
        'title': "SignIn"
    }
    return render(request, 'signin.html', context)


def signout(request):
    logout(request)
    messages.success(request, 'You Are Logged Out')
    return redirect('signin')


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = SignUpForm
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            form.save()
            user = form.cleaned_data.get('email')
            messages.success(
                request, f"Account Created Successfully for {user} ")
            return redirect('signin')
    context = {
        'form': form,
        'title': "SignUp"
    }
    return render(request, 'signup.html', context)
