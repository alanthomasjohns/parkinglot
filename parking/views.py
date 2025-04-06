from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ParkingLevel, ParkingSlot, VehicleType, Vehicle, ParkingRecord
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class ParkingAvailabilityView(APIView):
    """
    Returns real-time availability of slots per level and vehicle type,
    including available slot IDs
    """

    def get(self, request):
        levels_data = []

        levels = ParkingLevel.objects.all()
        vehicle_types = VehicleType.objects.all()

        for level in levels:
            slot_data = {}

            for v_type in vehicle_types:
                all_slots = ParkingSlot.objects.filter(level=level)
                available_slots = all_slots.filter(is_occupied=False)

                slot_data[v_type.name] = {
                    "total": all_slots.count(),
                    "available": available_slots.count(),
                    "slot_ids": list(
                        available_slots.values_list("slot_number", flat=True)
                    ),
                }

            levels_data.append({"level_number": level.level_number, "slots": slot_data})

        return Response({"levels": levels_data})


class AddVehicleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vehicle_type_id = request.data.get("vehicle_type_id")
        license_plate = request.data.get("license_plate")

        if not vehicle_type_id or not license_plate:
            return Response(
                {"error": "Vehicle type and license plate are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
        except VehicleType.DoesNotExist:
            return Response(
                {"error": "Invalid vehicle type."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already added
        if Vehicle.objects.filter(license_plate=license_plate.upper()).exists():
            return Response(
                {"error": "Vehicle already registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vehicle = Vehicle.objects.create(
            owner=request.user,
            vehicle_type=vehicle_type,
            license_plate=license_plate.upper(),
        )

        return Response(
            {
                "message": "Vehicle saved",
                "vehicle_id": vehicle.id,
                "vehicle_type": vehicle_type.name,
            },
            status=status.HTTP_201_CREATED,
        )


class AllocateParkingSlotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vehicle_id = request.data.get("vehicle_id")

        if not vehicle_id:
            return Response(
                {"error": "Vehicle ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
        except Vehicle.DoesNotExist:
            return Response(
                {"error": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND
            )

        vehicle_type = vehicle.vehicle_type

        slot = (
            ParkingSlot.objects.filter(vehicle_type=vehicle_type, is_occupied=False)
            .select_related("level")
            .order_by("level__level_number", "slot_number")
            .first()
        )

        if not slot:
            return Response(
                {"message": "No available slot found for this vehicle type."},
                status=status.HTTP_404_NOT_FOUND,
            )

        record = ParkingRecord.objects.create(vehicle=vehicle, slot=slot)

        slot.is_occupied = True
        slot.save()

        return Response(
            {
                "message": "Parking allocated",
                "level": slot.level.level_number,
                "slot": slot.slot_number,
                "record_id": record.id,
            },
            status=status.HTTP_201_CREATED,
        )
