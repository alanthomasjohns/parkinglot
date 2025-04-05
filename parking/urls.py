from django.urls import path
from .views import ParkingAvailabilityView

urlpatterns = [
    path('parking/availability/', ParkingAvailabilityView.as_view(), name="parking-availability"),
]
