from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import StudentSerializer,SubjectSerializer,PDFDocumentSerializer,LastmoduleSerializer
from accounts.models import CustomUser
from .models import Student,Subject,PDFDocument,Lastmodule
from rest_framework.permissions import IsAuthenticated
from .bunnycdn_utils import BunnyCDNUploader
from django.conf import settings

BUNNY_CDN_STORAGE_ZONE = settings.BUNNY_CDN_STORAGE_ZONE
BUNNY_CDN_URL = settings.BUNNY_CDN_URL
BUNNY_API_KEY = settings.BUNNY_API_KEY


bunny_cdn = BunnyCDNUploader(
    api_key=BUNNY_API_KEY,
    storage_zone=BUNNY_CDN_STORAGE_ZONE,
    base_url=BUNNY_CDN_URL,
)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_student(request):
    print("Data = ", request.data)
    
    user_id = request.data.get('user')
    user_instance = None
    
    if user_id:
        try:
            user_instance = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": f"User with id {user_id} does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Make a mutable copy of request.data for proper file handling
    data = request.data.copy()
    
    serializer = StudentSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        try:
            serializer.save(user=user_instance)
            return Response(
                {
                    "status": "ok",
                    "message": "Student data created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"Error during save: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": f"Error saving student: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response(
        {
            "status": "error",
            "message": "Student creation failed",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_students(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(
            {
                "status": "error",
                "message": f"User with id {user_id} does not exist"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    students = Student.objects.filter(user=user).select_related("user")
    serializer = StudentSerializer(students, many=True, context={'request': request})

    return Response(
        {
            "status": "ok",
            "message": f"Students for user {user.username}",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response(
            {"status": "error", "message": f"Student with id {student_id} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )

    # If updating the image, delete the old one before replacing
    if 'image' in request.FILES:
        if student.image:  
            student.image.delete(save=False)  # ✅ deletes old file from storage

    serializer = StudentSerializer(student, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "status": "ok",
                "message": "Student updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    return Response(
        {
            "status": "error",
            "message": "Student update failed",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response(
            {"status": "error", "message": f"Student with id {student_id} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )

    # ✅ Delete the image file if it exists
    if student.image:
        student.image.delete(save=False)

    student.delete()

    return Response(
        {"status": "ok", "message": f"Student {student_id} deleted successfully"},
        status=status.HTTP_200_OK
    )



@api_view(['POST'])
def create_subject(request):
    serializer = SubjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status":"ok","message":"subject created successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_subjects_by_user(request, user_id):
    subjects = Subject.objects.filter(user_id=user_id)
    serializer = SubjectSerializer(subjects, many=True)
    return Response({
        "status": "ok",
        "message": "Subjects fetched successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
def update_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response(
            {"status": "error", "message": "Subject not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # partial=True allows partial updates (PATCH)
    serializer = SubjectSerializer(subject, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"status": "ok", "message": "Subject updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response(
            {"status": "error", "message": "Subject not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    subject.delete()
    return Response(
        {"status": "ok", "message": "Subject deleted successfully"},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def upload_pdf_document(request):
    serializer = PDFDocumentSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            pdf_doc = serializer.save()
            return Response({
                "status": "ok",
                "message": "PDF/PPT uploaded successfully (replaced if existing).",
                "data": PDFDocumentSerializer(pdf_doc, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Failed to upload file: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "status": "error",
        "message": "Invalid upload data.",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
def edit_pdf_document(request, pk):
    """
    Update a PDFDocument record.
    - If new files (PDF/PPT) are uploaded, they replace the old ones on BunnyCDN.
    - Other fields like subject/module_name can also be updated.
    """
    try:
        pdf_doc = PDFDocument.objects.get(pk=pk)
    except PDFDocument.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Document not found."
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = PDFDocumentSerializer(pdf_doc, data=request.data, context={'request': request}, partial=True)

    if serializer.is_valid():
        try:
            updated_doc = serializer.save()
            return Response({
                "status": "ok",
                "message": "PDF/PPT updated successfully.",
                "data": PDFDocumentSerializer(updated_doc, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Failed to update file: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        "status": "error",
        "message": "Invalid update data.",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_pdf_document(request, pk):
    """
    Delete a PDFDocument and its files from BunnyCDN.
    """
    try:
        pdf_doc = PDFDocument.objects.get(pk=pk)
    except PDFDocument.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Document not found."
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        # Delete from BunnyCDN if files exist
        if pdf_doc.file:
            deleted_pdf = bunny_cdn.delete_file(pdf_doc.file)

        if pdf_doc.ppt_file:
            deleted_ppt = bunny_cdn.delete_file(pdf_doc.ppt_file)

        # Delete the database record
        pdf_doc.delete()

        return Response({
            "status": "ok",
            "message": "Document and associated files deleted successfully."
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Failed to delete: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def pdf_list_by_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"Subject with id {subject_id} does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    pdfs = PDFDocument.objects.filter(subject=subject).order_by('-uploaded_at')

    serializer = PDFDocumentSerializer(pdfs, many=True, context={'request': request})
    return Response({
        "status": "ok",
        "subject": subject.name,
        "count": pdfs.count(),
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def lastmodule_replace_view(request):
    lastmodule = Lastmodule.objects.first()

    if lastmodule:
        serializer = LastmoduleSerializer(lastmodule, data=request.data, context={'request': request})
    else:
        serializer = LastmoduleSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        instance = serializer.save()
        return Response(LastmoduleSerializer(instance, context={'request': request}).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def lastmodule_list_view(request):
    lastmodule = Lastmodule.objects.first()
    if not lastmodule:
        return Response({"detail": "No Lastmodule found"}, status=404)

    serializer = LastmoduleSerializer(lastmodule, context={'request': request})  # ✅ pass request
    return Response(serializer.data)