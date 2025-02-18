from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AktivitetsTeamBookingViewSet

router = DefaultRouter()
router.register(r'bookings', AktivitetsTeamBookingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]