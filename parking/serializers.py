from rest_framework import serializers
from .models import (
    VehicleType,
    ParkingLevel,
    ParkingSlot,
    Vehicle,
    ParkingRecord
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
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_type', 'license_plate']
        read_only_fields = ['id']


class ParkingRecordSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(source='slot.level.level_number', read_only=True)
    slot_number = serializers.CharField(source='slot.slot_number', read_only=True)
    vehicle = serializers.StringRelatedField()

    class Meta:
        model = ParkingRecord
        fields = ['id', 'vehicle', 'level', 'slot_number', 'entry_time', 'exit_time']
        read_only_fields = ['id', 'entry_time', 'exit_time']

    def validate(self, data):
        vehicle = data.get('vehicle')
        if ParkingRecord.objects.filter(vehicle=vehicle, exit_time__isnull=True).exists():
            raise serializers.ValidationError("This vehicle already has an active parking record.")
        return data
