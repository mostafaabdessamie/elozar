from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include
from django.views.static import serve

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('service-worker.js', serve, {
        'document_root': settings.BASE_DIR / 'static',
        'path': 'service-worker.js'
    }),
    path('manifest.json', serve, {
        'document_root': settings.BASE_DIR / 'static', 
        'path': 'manifest.json'
    }),
    
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('admin/', admin.site.urls),

    path('', include('home.urls')),
    path('users/', include('users.urls')),
    path('core/', include('core.urls')),
    path('cours/', include('cours.urls')),
    path('book/', include('book.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)