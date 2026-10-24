from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('loi/', views.loi08_09, name='loi08_09'),
   
]