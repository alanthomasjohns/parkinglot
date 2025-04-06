from django.urls import path
from .views import ParkingAvailabilityView, AddVehicleView, AllocateParkingSlotView

urlpatterns = [
    path('parking/availability/', ParkingAvailabilityView.as_view(), name="parking-availability"),
    path('vehicle/', AddVehicleView.as_view(), name="add-vehicle"),
    path('parking/allocate/', AllocateParkingSlotView.as_view(), name="allocate-parking"),  # ✅ Fix here
]
