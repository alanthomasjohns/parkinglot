from django.contrib import admin
from .models import VehicleType, ParkingLevel, ParkingSlot, Vehicle, Reservation

# Register your models here.

admin.site.register([VehicleType, ParkingLevel, ParkingSlot, Vehicle, Reservation])