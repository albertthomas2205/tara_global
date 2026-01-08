from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Person,Appointment
from .serializers import PersonSerializer,AppointmentSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def person_list(request):
    persons = Person.objects.filter(user=request.user)
    
    # ✅ Add pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # default items per page
    result_page = paginator.paginate_queryset(persons, request)
    serializer = PersonSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(
        {
            "status": "ok",
            "message": "Person list fetched successfully",
            "data": serializer.data
        }
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # ✅ attach the logged-in user automatically
        return Response(
            {
                "status": "ok",
                "message": "Appointment created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(
        {
            "status": "error",
            "message": "Invalid data",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_appointments(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('-id')  # newest first
    
    # ✅ Add pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # you can adjust this
    result_page = paginator.paginate_queryset(appointments, request)
    serializer = AppointmentSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(
        {
            "status": "ok",
            "message": "Appointments fetched successfully",
            "count": appointments.count(),
            "data": serializer.data
        }
    )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, pk):
    try:
        # ✅ Ensure only logged-in user's appointments are accessible
        appointment = Appointment.objects.get(pk=pk, user=request.user)
    except Appointment.DoesNotExist:
        return Response(
            {
                "status": "error",
                "message": "Appointment not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AppointmentSerializer(appointment)
    return Response(
        {
            "status": "ok",
            "message": "Appointment details fetched successfully",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )