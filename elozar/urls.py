from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('admin/', admin.site.urls),

    path('', include('home.urls')),

    path('users/', include('users.urls')),
    path('core/', include('core.urls')),
    
    path('cours/', include('cours.urls')),
    path('book/', include('book.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)