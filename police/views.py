from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Complaint,Speak
from .serializers import ComplaintSerializer,SpeakSerializer
from rest_framework.pagination import PageNumberPagination
@api_view(['POST'])
def create_complaint(request):
    serializer = ComplaintSerializer(data=request.data)
    if serializer.is_valid():
        complaint = serializer.save()  # case_id is auto-set in model's save()
        return Response({
            "status": "ok",
            "message": "Complaint created successfully.",
            "data": ComplaintSerializer(complaint).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "failed",
        "message": "Validation error.",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


class ComplaintPagination(PageNumberPagination):
    page_size = 5  # you can adjust this
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
def get_user_complaints_paginated(request):
    user_id = request.query_params.get('user')

    if not user_id:
        return Response({
            "status": "failed",
            "message": "Missing 'user' parameter."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        complaints = Complaint.objects.filter(user_id=user_id).order_by('-created_at')
        paginator = ComplaintPagination()
        paginated_complaints = paginator.paginate_queryset(complaints, request)
        serializer = ComplaintSerializer(paginated_complaints, many=True)

        return paginator.get_paginated_response({
            "status": "ok",
            "message": "Complaints retrieved successfully.",
            "data": serializer.data
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": "An error occurred while retrieving complaints.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT', 'PATCH'])
def update_complaint_by_case_id(request, case_id):
    try:
        complaint = Complaint.objects.get(case_id=case_id)
    except Complaint.DoesNotExist:
        return Response({
            "status": "failed",
            "message": f"No complaint found with case_id '{case_id}'"
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = ComplaintSerializer(complaint, data=request.data, partial=True)  # Use partial=True to allow partial updates

    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "ok",
            "message": "Complaint updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "failed",
        "message": "Validation failed.",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_last_case_id_by_user(request):
    user_id = request.query_params.get('user')

    if not user_id:
        return Response({
            "status": "failed",
            "message": "Missing 'user' parameter."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        last_complaint = Complaint.objects.filter(user_id=user_id).order_by('-created_at').first()
        
        if last_complaint:
            return Response({
                "status": "ok",
                "message": "Last case ID retrieved successfully.",
                "data": {
                    "case_id": last_complaint.case_id,
                    "name":last_complaint.name,
                    "age":last_complaint.age,
                    "address":last_complaint.address


                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "ok",
                "message": "No complaints found for this user.",
                "data": None
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "status": "error",
            "message": "An error occurred while retrieving the last case ID.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def create_speak(request):
    # Delete all existing Speak objects
    Speak.objects.all().delete()

    # Create the new one
    serializer = SpeakSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Speak object created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": "failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_speak(request):
    speaks = Speak.objects.all()
    serializer = SpeakSerializer(speaks, many=True)
    return Response({
        "status": "success",
        
        "data": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def complaint_detail(request, case_id):
    try:
        complaint = Complaint.objects.get(case_id=case_id)
        serializer = ComplaintSerializer(complaint)
        return Response({
            "status": "ok",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Complaint.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Complaint not found."
        }, status=status.HTTP_404_NOT_FOUND)