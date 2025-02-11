from django.shortcuts import render

# Create your views here.

def no_permission(request):
    return render(request, 'no_permission.html')