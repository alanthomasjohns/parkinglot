from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ParkingLevel, ParkingSlot, VehicleType


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
                all_slots = ParkingSlot.objects.filter(level=level, slot_type=v_type)
                available_slots = all_slots.filter(is_occupied=False)

                slot_data[v_type.name] = {
                    "total": all_slots.count(),
                    "available": available_slots.count(),
                    "slot_ids": list(available_slots.values_list('slot_number', flat=True))
                }

            levels_data.append({
                "level_number": level.level_number,
                "slots": slot_data
            })

        return Response({"levels": levels_data})
