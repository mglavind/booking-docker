from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Protect the view with login_required
    path('', include('AktivitetsTeam.urls')),
]

