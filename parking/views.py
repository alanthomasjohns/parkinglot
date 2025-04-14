from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ParkingLevel, ParkingSlot, VehicleType, Vehicle, ParkingRecord
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from django.utils import timezone


class ParkingAvailabilityView(APIView):
    """
    Returns real-time availability of parking slots per level.
    """

    def get(self, request):
        levels_data = []

        levels = ParkingLevel.objects.all()

        for level in levels:
            available = []
            occupied = []

            all_slots = ParkingSlot.objects.filter(level=level).select_related(
                "vehicle_type"
            )

            for slot in all_slots:
                slot_info = {
                    "slot_id": slot.slot_number,
                    "vehicle_type": slot.vehicle_type.name,
                }
                if slot.is_occupied:
                    occupied.append(slot_info)
                else:
                    available.append(slot_info)

            if available or occupied:
                levels_data.append(
                    {
                        "level_number": level.level_number,
                        "slots": {"available": available, "occupied": occupied},
                    }
                )

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
        license_plate = request.data.get("license_plate")
        slot_number = request.data.get("slot_number")

        if not license_plate or not slot_number:
            return Response(
                {"error": "Both license plate and slot number are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            vehicle = get_object_or_404(
                Vehicle, license_plate=license_plate, owner=request.user
            )
        except Vehicle.DoesNotExist:
            return Response(
                {"error": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if ParkingRecord.objects.filter(
            vehicle=vehicle, exit_time__isnull=True
        ).exists():
            return Response(
                {"error": "Vehicle is already parked."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            slot = ParkingSlot.objects.select_related("level").get(
                slot_number=slot_number,
                vehicle_type=vehicle.vehicle_type,
                is_occupied=False,
            )
        except ParkingSlot.DoesNotExist:
            return Response(
                {"error": "Slot not available or does not match vehicle type."},
                status=status.HTTP_404_NOT_FOUND,
            )

        record = ParkingRecord.objects.create(vehicle=vehicle, slot=slot)

        slot.is_occupied = True
        slot.save(update_fields=["is_occupied"])

        return Response(
            {
                "message": "Parking allocated",
                "level": slot.level.level_number,
                "slot": slot.slot_number,
                "record_id": record.id,
            },
            status=status.HTTP_201_CREATED,
        )



class CheckoutParkingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vehicle_id = request.data.get("vehicle_id")
        license_plate = request.data.get("license_plate")

        try:
            if vehicle_id:
                vehicle = Vehicle.objects.get(id=vehicle_id, owner=request.user)
            elif license_plate:
                vehicle = Vehicle.objects.get(
                    license_plate=license_plate.upper(), owner=request.user
                )
            else:
                return Response(
                    {"error": "vehicle_id or license_plate is required."}, status=400
                )

            parking_record = (
                ParkingRecord.objects.filter(vehicle=vehicle, exit_time__isnull=True)
                .order_by("-created")
                .first()
            )
            if not parking_record:
                return Response(
                    {"error": "No active parking record found."}, status=404
                )

        except Vehicle.DoesNotExist:
            return Response({"error": "Vehicle not found."}, status=404)

        parking_record.exit_time = timezone.now()

        slot = parking_record.slot
        slot.is_occupied = False
        slot.save(update_fields=["is_occupied"])

        duration = parking_record.exit_time - parking_record.entry_time
        hours = max(1, int(duration.total_seconds() // 3600))  # Charge at least 1 hour
        rate_per_hour = 20  # ₹20 per hour
        amount = hours * rate_per_hour
        parking_record.amount = amount
        parking_record.payment_status = "PENDING"

        details = {
            "message": "Please complete payment to exit.",
            "license_plate": vehicle.license_plate.upper(),
            "entry_time": parking_record.entry_time.isoformat(),
            "exit_time": parking_record.exit_time.isoformat(),
            "duration_hours": hours,
            "amount": amount,
            "payment_status": parking_record.payment_status,
        }
        parking_record.payment_details = details
        parking_record.save(
            update_fields=["exit_time", "amount", "payment_status", "payment_details"]
        )

        return Response(
            details,
            status=status.HTTP_200_OK,
        )


class MarkPaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        parking_record_id = request.data.get("parking_record_id")
        license_plate = request.data.get("license_plate")

        if parking_record_id:
            parking_record = (
                ParkingRecord.objects.filter(
                    id=parking_record_id, vehicle__owner=request.user
                )
                .order_by("-created")
                .first()
            )
        elif license_plate:
            parking_record = (
                ParkingRecord.objects.filter(
                    vehicle__license_plate=license_plate, vehicle__owner=request.user
                )
                .order_by("-created")
                .first()
            )
        else:
            return Response({"error": "Number plate / ID should be provided"})
        if not parking_record:
            return Response({"error": "Parking record not found"})

        if parking_record.payment_status == "SUCCESS":
            return Response({"message": "Payment already completed."})

        parking_record.payment_status = "SUCCESS"
        details = parking_record.payment_details or {}
        details["payment_status"] = "SUCCESS"
        details["paid_on"] = str(timezone.now())
        details["message"] = "Payment Completed"
        parking_record.payment_details = details
        parking_record.save(update_fields=["payment_status", "payment_details"])

        return Response({
            "message": "Payment marked as successful.",
            "invoice_details": parking_record.payment_details
            })
