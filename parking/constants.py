from django.db import models


class VehicleCategory(models.TextChoices):
    TWO_WHEELER = "2-wheeler", "2-Wheeler"
    FOUR_WHEELER = "4-wheeler", "4-Wheeler"
    HEAVY_LOAD = "heavy-load", "Heavy Load"
