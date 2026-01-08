from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Navigation
from .serializers import *
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from education.bunnycdn_utils import BunnyCDNUploader
from django.conf import settings
import requests

# Create your views here.
@api_view(['POST'])
def create_navigation(request):
    serializer = NavigationSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        try:
            serializer.save()
            return Response(
                {
                    "status": "ok",
                    "message": "Navigation created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Error saving navigation: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response(
        {"status": "error", "message": "Navigation creation failed", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
def list_navigation(request):
    robot = request.query_params.get('robot', None)  # ?robot=R1
    page = request.query_params.get('page', 1)       # ?page=1
    page_size = int(request.query_params.get('page_size', 10))  # ensure int

    if robot:
        navigations = Navigation.objects.filter(robot=robot)
    else:
        navigations = Navigation.objects.all()

    paginator = Paginator(navigations, page_size)

    try:
        navigations_page = paginator.page(page)
    except PageNotAnInteger:
        navigations_page = paginator.page(1)
    except EmptyPage:
        navigations_page = paginator.page(paginator.num_pages)

    serializer = NavigationSerializer(navigations_page, many=True, context={'request': request})

    return Response({
        "status": "ok",
        "message": "Navigation list fetched successfully",
        "data": serializer.data,
        "pagination": {
            "current_page": navigations_page.number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "page_size": paginator.per_page,
            "items_in_page": len(navigations_page)   # ✅ how many items in this page
        }
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
def edit_navigation(request, pk):
    """
    Allows authenticated users to update an existing navigation entry.
    Supports file uploads and direct URL updates for image/video.
    """
    try:
        navigation = Navigation.objects.get(id=pk)
    except Navigation.DoesNotExist:
        return Response({"error": "Navigation not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = NavigationSerializer(
        navigation, data=request.data, partial=True, context={'request': request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "status": "ok",
                "message": "Navigation updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def navigation_detail(request, navigation_id):
    """
    Retrieve a Navigation record by navigation_id instead of primary key.
    """
    navigation = get_object_or_404(Navigation, navigation_id=navigation_id)
    serializer = NavigationSerializer(navigation, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


bunny_cdn = BunnyCDNUploader(
    api_key=settings.BUNNY_API_KEY,
    storage_zone=settings.BUNNY_CDN_STORAGE_ZONE,
    base_url=settings.BUNNY_CDN_URL,
)

@api_view(['DELETE'])
def delete_navigation_by_robot(request, robot_id):
    """
    Delete all Navigation records for a given robot_id,
    including their images and videos from BunnyCDN.
    """
    # Filter navigations belonging to the given robot
    navigations = Navigation.objects.filter(robot=robot_id)

    if not navigations.exists():
        return Response(
            {"message": f"No navigations found for robot_id {robot_id}"},
            status=status.HTTP_404_NOT_FOUND
        )

    deleted_count = 0
    for nav in navigations:
        # Delete image from BunnyCDN if exists
        if nav.image:
            try:
                # Extract the path after storage URL
                path = nav.image.replace(bunny_cdn.base_url + "/", "")
                delete_url = f"https://storage.bunnycdn.com/{bunny_cdn.storage_zone}/{path}"
                requests.delete(delete_url, headers={"AccessKey": bunny_cdn.api_key}, timeout=10)
            except Exception as e:
                print(f"Failed to delete image from BunnyCDN: {str(e)}")

        # Delete video from BunnyCDN if exists
        if nav.video:
            try:
                path = nav.video.replace(bunny_cdn.base_url + "/", "")
                delete_url = f"https://storage.bunnycdn.com/{bunny_cdn.storage_zone}/{path}"
                requests.delete(delete_url, headers={"AccessKey": bunny_cdn.api_key}, timeout=10)
            except Exception as e:
                print(f"Failed to delete video from BunnyCDN: {str(e)}")

        # Delete DB record
        nav.delete()
        deleted_count += 1

    return Response(
        {"message": f"{deleted_count} navigation(s) deleted successfully"},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_full_tour(request):
    robot = request.data.get('robot')
    navigations = request.data.get('navigations', [])

    if not robot:
        return Response({"error": "Robot is required."}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(navigations, list):
        return Response({"error": "Invalid data format. Navigations must be a list of IDs."}, status=status.HTTP_400_BAD_REQUEST)

    # Replace or create FullTour for this robot
    full_tour, _ = FullTour.objects.update_or_create(
        robot=robot,
        defaults={"navigations": navigations}
    )

    serializer = FullTourSerializer(full_tour)
    return Response(
        {"status": "ok", "message": "Full tour created successfully", "data": serializer.data},
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def full_tour_list(request):
    robot = request.query_params.get("robot")  

    if robot:
        # Return only the specific robot's tour
        try:
            full_tour = FullTour.objects.get(robot=robot)
        except FullTour.DoesNotExist:
            return Response({"status": "ok", "data": None}, status=status.HTTP_200_OK)

        serializer = FullTourSerializer(full_tour)
        return Response({"status": "ok", "data": serializer.data}, status=status.HTTP_200_OK)

    else:
        # Return all tours
        full_tours = FullTour.objects.all()
        serializer = FullTourSerializer(full_tours, many=True)
        return Response({"status": "ok", "data": serializer.data}, status=status.HTTP_200_OK)
    


@api_view(['GET'])
def full_tour_by_robot(request, robot):
    try:
        full_tour = FullTour.objects.get(robot=robot)
    except FullTour.DoesNotExist:
        return Response({"status": "ok", "data": None}, status=status.HTTP_200_OK)

    serializer = FullTourSerializer(full_tour)
    return Response({"status": "ok", "data": serializer.data}, status=status.HTTP_200_OK)



MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB in bytes

@api_view(["POST"])
def create_or_update_display_video(request):
    robot = request.data.get("robot")

    if not robot:
        return Response({"error": "robot field is required"}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Check if video file exists and enforce 50MB size limit
    video_file = request.FILES.get("video")
    if video_file and video_file.size > MAX_VIDEO_SIZE:
        return Response(
            {"error": "Video file size exceeds 50 MB limit"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if a record with the same robot exists
    instance = DisplayVideo.objects.filter(robot=robot).first()

    if instance:
        # Update existing record
        serializer = DisplayVideoSerializer(
            instance, data=request.data, context={"request": request}, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create a new record
    serializer = DisplayVideoSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response({"status":"ok","message":"data created successfully","data":serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def list_display_videos(request):
    robot = request.query_params.get("robot", None)

    if robot:
        videos = DisplayVideo.objects.filter(robot=robot)
    else:
        videos = DisplayVideo.objects.all()

    if videos.exists():
        video = videos.first()  # pick the first video
        serializer = DisplayVideoSerializer(video, context={"request": request})
        data = serializer.data
    else:
        data = {}

    return Response({
        "status": "ok",
        "message": "data retrieved successfully",
        "data": data  # this will be a single object, not a list
    }, status=status.HTTP_200_OK)



@api_view(["DELETE"])
def delete_display_video(request, pk):
    try:
        video = DisplayVideo.objects.get(pk=pk)
    except DisplayVideo.DoesNotExist:
        return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Try removing from BunnyCDN
    deleted = bunny_cdn.delete_file(video.video)
    if not deleted:
        return Response(
            {"warning": "Video record removed, but BunnyCDN file could not be deleted"},
            status=status.HTTP_200_OK
        )

    # ✅ Remove DB record
    video.delete()
    return Response({"message": "Video deleted successfully"}, status=status.HTTP_204_NO_CONTENT)