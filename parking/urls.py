from django.urls import path
from .views import (
    ParkingAvailabilityView,
    AddVehicleView,
    AllocateParkingSlotView,
    CheckoutParkingView,
    MarkPaymentSuccessView,
)

urlpatterns = [
    path("availability/", ParkingAvailabilityView.as_view(), name="parking-availability"),
    path("vehicle/", AddVehicleView.as_view(), name="add-vehicle"),
    path("allocate/", AllocateParkingSlotView.as_view(), name="allocate-parking"),
    path("checkout/", CheckoutParkingView.as_view(), name="parking-checkout"),
    path("payment/", MarkPaymentSuccessView.as_view(), name="parking-payment"),
]