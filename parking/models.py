from django.db import models
from accounts.models import User


class VehicleType(models.Model):
    """
    Represents different types of vehicles that can use the parking system.
    Example: Motorcycle, Car, Bus.
    """
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name}"


class ParkingLevel(models.Model):
    """
    Represents a floor or level in the multi-level parking structure.
    Each level can have multiple parking slots.
    """
    level_number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Level {self.level_number}"


class ParkingSlot(models.Model):
    """
    Represents an individual parking slot within a specific level,
    assigned to a certain vehicle type.
    """
    slot_number = models.CharField(max_length=10)
    level = models.ForeignKey(ParkingLevel, on_delete=models.CASCADE, related_name='slots')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Slot {self.slot_number} (Level {self.level.level_number})"


class Vehicle(models.Model):
    """
    Stores details of vehicles registered by users.
    Used for reservation, assignment, and billing.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.license_plate} ({self.vehicle_type.name})"


class Reservation(models.Model):
    """
    Represents a reservation made by a user for a parking slot.
    Helps in pre-booking, billing, and managing slot availability.
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    reserved_from = models.DateTimeField()
    reserved_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Reservation for {self.vehicle} from {self.reserved_from} to {self.reserved_to}"
