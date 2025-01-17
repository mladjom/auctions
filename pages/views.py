# pages/view.py
from django.shortcuts import render

def home(request):
    # Add any logic for the homepage if necessary
    return render(request, 'pages/home.html')

def about(request):
    # Add any logic for the about page if necessary
    return render(request, 'pages/about.html')

def contact(request):
    # Add any logic for the contact page if necessary
    return render(request, 'pages/contact.html')

def terms(request):
    return render(request, 'pages/terms.html')

def privacy(request):
    return render(request, 'pages/privacy.html')


