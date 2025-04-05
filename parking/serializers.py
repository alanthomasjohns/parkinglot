from rest_framework import serializers
from .models import (
    VehicleType,
    ParkingLevel,
    ParkingSlot,
    Vehicle,
    Reservation
)


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'


class ParkingLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLevel
        fields = '__all__'


class ParkingSlotSerializer(serializers.ModelSerializer):
    level = ParkingLevelSerializer(read_only=True)

    class Meta:
        model = ParkingSlot
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    slot = ParkingSlotSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'
