from django.urls import path
from . import views

urlpatterns = [
    path('', views.livre_list, name='livre_list'),
    path('<int:pk>/', views.livre_detail, name='livre_detail'),
    path('ajouter/', views.livre_create, name='livre_create'),
    path('<int:pk>/modifier/', views.livre_update, name='livre_update'),
    path('<int:pk>/supprimer/', views.livre_delete, name='livre_delete'),
]