from django.shortcuts import render

def home(request):
    
    return render(request, 'home/home.html')


def about(request):
    
    return render(request, 'home/about.html')

def loi08_09(request):
    return render(request, 'home/loi08-09.html')