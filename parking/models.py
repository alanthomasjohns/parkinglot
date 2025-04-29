from django.db import models
from accounts.models import User
from .constants import VehicleCategory
from django.utils import timezone
from django.core.exceptions import ValidationError


class VehicleType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    category = models.CharField(
        max_length=20, choices=VehicleCategory.choices, null=True, blank=True
    )

    def __str__(self):
        return self.name


class ParkingLevel(models.Model):
    level_number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Level {self.level_number}"


class ParkingSlot(models.Model):
    slot_number = models.CharField(max_length=10)
    level = models.ForeignKey(
        ParkingLevel, on_delete=models.CASCADE, related_name="slots"
    )
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    is_occupied = models.BooleanField(default=False)
    is_prebooked = models.BooleanField(default=False)

    def __str__(self):
        return f"Slot {self.slot_number} (Level {self.level.level_number})"


class Vehicle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.license_plate} ({self.vehicle_type.name})"


class ParkingRecord(models.Model):
    """
    Real-time parking record for tracking entry/exit and billing.
    """

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("PENDING", "Pending"), ("SUCCESS", "Success"), ("FAILED", "Failed")],
        default="PENDING",
        null=True,
    )
    payment_details = models.JSONField(default=dict, null=True, blank=True)
    created = models.DateTimeField(("Created"), auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.vehicle} - Slot {self.slot.slot_number} | {self.entry_time} ➡ {self.exit_time or 'Active'}"

    @property
    def is_active(self):
        return self.exit_time is None

    def clean(self):
        if not self.exit_time:
            existing = ParkingRecord.objects.filter(
                vehicle=self.vehicle, exit_time__isnull=True
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(
                    "An active parking record already exists for this vehicle."
                )
