from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Protect the view with login_required
    path('organization/', include('organization.urls')),
    path('butikken/', include('Butikken.urls')),
    path('aktivitetsteam/', include('AktivitetsTeam.urls')),
    path('sjak/', include('Sjak.urls')),
    path('teknik/', include('Teknik.urls')),
    path('SOS/', include('SOS.urls')),
    path('foto/', include('Foto.urls')),
    
    # NEW: Comments URLs
    path('comments/', include('django_comments_xtd.urls')),
    path('comments/', include('django_comments.urls')),
]

