from django.shortcuts import render

def home(request):
    
    return render(request, 'home/home.html')

#  معلومات حول السونتر
def about(request):
    
    return render(request, 'home/about.html')