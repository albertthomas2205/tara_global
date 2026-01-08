from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import *
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()
import os
from django.utils.timezone import now
from django.core.files.storage import default_storage
from django.utils import timezone

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_patient(request):
    # Only allow users with role_type HOSPITAL
    if request.user.role_type != 'HOSPITAL':
        return Response({
            "status": "error",
            "message": "You are not authorized to perform this action"
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = PatientSerializer(data=request.data)
    if serializer.is_valid():
        # Automatically attach logged-in user
        serializer.save(user=request.user)
        return Response({
            "status": "ok",
            "message": "Patient created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "error",
        "message": "Failed to create patient",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_patients_by_user(request, user_id):
    patients = Patient.objects.filter(user_id=user_id)
    serializer = PatientSerializer(patients, many=True)

    return Response({
        "status": "ok",
        "message": "Patients retrieved successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_patient(request, pk):
    # Only allow users with role_type HOSPITAL
    if request.user.role_type != 'HOSPITAL':
        return Response({
            "status": "error",
            "message": "You are not authorized to perform this action"
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        patient = Patient.objects.get(pk=pk, user=request.user)
    except Patient.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Patient not found or not owned by you"
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = PatientSerializer(patient, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "ok",
            "message": "Patient updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "error",
        "message": "Failed to update patient",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_detail(request, pk):
    # Only allow users with role_type HOSPITAL
    if request.user.role_type != 'HOSPITAL':
        return Response({
            "status": "error",
            "message": "You are not authorized to perform this action"
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        patient = Patient.objects.get(pk=pk, user=request.user)
    except Patient.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Patient not found or not associated with you"
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = PatientSerializer(patient)
    return Response({
        "status": "ok",
        "message": "Patient detail retrieved successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_patient(request, pk):
    # Only allow users with role_type HOSPITAL
    if request.user.role_type != 'HOSPITAL':
        return Response({
            "status": "error",
            "message": "You are not authorized to perform this action"
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        patient = Patient.objects.get(pk=pk, user=request.user)
    except Patient.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Patient not found or not associated with you"
        }, status=status.HTTP_404_NOT_FOUND)

    patient.delete()
    return Response({
        "status": "ok",
        "message": "Patient deleted successfully"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_room(request):
    """Create a new room ensuring same robot doesn't reuse same room_number."""
    data = request.data.copy()
    data['is_available'] = True  # Always set true on creation

    room_number = data.get('room_number')
    robot = data.get('robot')

    if Room.objects.filter(room_number=room_number, robot=robot).exists():
        return Response({
            "status": "error",
            "message": "Room with this number already exists for the same robot."
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = RoomSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "ok",
            "message": "Room created successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def list_rooms_by_robot(request, robot):
    """List rooms filtered by robot name passed in the URL."""
    rooms = Room.objects.filter(robot=robot)
    serializer = RoomSerializer(rooms, many=True)
    return Response({
        "status": "ok",
        "data": serializer.data
    })

@api_view(['DELETE'])
def delete_rooms_by_robot(request, robot_id):
    rooms = Room.objects.filter(robot=robot_id)
    
    if not rooms.exists():
        return Response({'error': 'No rooms found with this robot ID'}, status=status.HTTP_404_NOT_FOUND)
    
    count = rooms.count()
    rooms.delete()
    
    # ✅ Use 200 to ensure the message is sent
    return Response({'message': f'{count} room(s) deleted for robot ID: {robot_id}'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def assign_patient_to_room(request, user_id):
    # Validate user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": "User not found."
        }, status=status.HTTP_404_NOT_FOUND)

    # Extract patient_id and room_id from request
    patient_id = request.data.get("patient")
    room_id = request.data.get("room")
    text = request.data.get("text", "")

    # Fetch patient & room
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({"status": "error", "message": "Patient not found."}, status=404)

    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({"status": "error", "message": "Room not found."}, status=404)

    # Check if already assigned
    if PatientRoomAssignment.objects.filter(patient=patient).exists():
        return Response({"status": "error", "message": "This patient is already assigned."}, status=400)

    if PatientRoomAssignment.objects.filter(room=room).exists():
        return Response({"status": "error", "message": "This room is already occupied."}, status=400)

    if not room.is_available:
        return Response({"status": "error", "message": "This room is not available."}, status=400)

    # Create assignment
    assignment = PatientRoomAssignment.objects.create(
        patient=patient,
        room=room,
        user=user,
        text=text
    )

    # Update statuses
    room.is_available = False
    room.save()
    patient.status = False
    patient.save()

    # Serialize with nested details
    response_serializer = PatientRoomAssignmentSerializer(assignment, context={'request': request})

    return Response({
        "status": "ok",
        "message": "Room assigned successfully.",
        "data": response_serializer.data
    }, status=status.HTTP_201_CREATED)



@api_view(['GET'])
def list_patient_room_assignments(request, user_id):
    assignments = PatientRoomAssignment.objects.select_related('patient', 'room') \
                                               .filter(user_id=user_id)
    serializer = PatientRoomAssignmentSerializer(assignments, many=True, context={'request': request})
    
    return Response({
        "status": "ok",
        "message": "data retrieved successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)



@api_view(['PUT'])
def update_patient_room_assignment(request, pk):
    try:
        assignment = PatientRoomAssignment.objects.get(pk=pk)
    except PatientRoomAssignment.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Patient room assignment not found."
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = PatientRoomAssignmentSerializer(
        assignment,
        data=request.data,
        partial=True,
        context={'request': request}
    )

    if serializer.is_valid():
        # ✅ Save normally first
        updated_assignment = serializer.save()

        # ✅ If a new PDF file is provided, update it
        if 'pdf' in request.FILES:
            updated_assignment.pdf = request.FILES['pdf']
            updated_assignment.save()

        return Response({
            "status": "ok",
            "message": "Assignment updated successfully.",
            "data": PatientRoomAssignmentSerializer(updated_assignment, context={'request': request}).data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_patient_room_assignment_detail(request, pk):
    try:
        assignment = PatientRoomAssignment.objects.get(pk=pk)
    except PatientRoomAssignment.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Patient room assignment not found."
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = PatientRoomAssignmentSerializer(assignment, context={'request': request})
    return Response({
        "status": "ok",
        "message": "Assignment retrieved successfully.",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_patient_room_assignment(request, pk):
    try:
        assignment = PatientRoomAssignment.objects.get(pk=pk)
    except PatientRoomAssignment.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Patient room assignment not found."
        }, status=status.HTTP_404_NOT_FOUND)

    # Mark the room as available again
    assignment.room.is_available = True
    assignment.room.save()

    # ✅ Set the patient's status back to True
    assignment.patient.status = True
    assignment.patient.save()

   

    # Store the deletion time
    deletion_time = now()

    # Delete the assignment
    assignment.delete()

    return Response({
        "status": "ok",
        "message": "Assignment deleted successfully.",
        "deleted_at": deletion_time.strftime("%Y-%m-%d %H:%M:%S")
    }, status=status.HTTP_200_OK)





@api_view(['PUT'])
def update_assignment_text_by_room(request, room_number):
    try:
        assignment = PatientRoomAssignment.objects.get(room__room_number=room_number)
    except PatientRoomAssignment.DoesNotExist:
        return Response({'detail': 'Assignment not found for this room.'}, status=status.HTTP_404_NOT_FOUND)

    new_text = request.data.get('text')
    if not new_text:
        return Response({'text': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Get local time instead of UTC
    local_time = timezone.localtime(timezone.now())
    current_time_str = local_time.strftime("%d-%m-%Y %I:%M %p") 
    

    # ✅ Add timestamp to the new text
    timestamped_text = f"{new_text} (updated at {current_time_str})"

    # ✅ Append new text above existing history
    if assignment.text:
        assignment.text = f"{timestamped_text}\n{assignment.text}"
    else:
        assignment.text = timestamped_text

    assignment.save()

    serializer = AssignmentTextUpdateSerializer(assignment)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def assignment_detail_by_room_number(request, room_number):
    try:
        assignment = PatientRoomAssignment.objects.get(room__room_number=room_number)
    except PatientRoomAssignment.DoesNotExist:
        return Response({'detail': 'No assignment found for this room number.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PatientRoomAssignmentSerializer(assignment, context={'request': request})
    return Response({"status":"ok","message":"data retrieved successfully","data":serializer.data})
