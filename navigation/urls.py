from django.urls import path
from .views import *


urlpatterns = [
    path('navigation/create/', create_navigation, name='create-navigation'),
    path('navigation/list/', list_navigation, name='list_navigation'),
    path('navigation/edit/<int:pk>/', edit_navigation, name='edit_navigation'),
    path('navigation/detail/<str:navigation_id>/', navigation_detail, name='navigation-detail'),
    path('navigation/delete/<str:robot_id>/', delete_navigation_by_robot, name='delete-navigation-by-robot'),

    path('full_tour/create/', create_full_tour, name='create_full_tour'),
    path('full_tour/list/', full_tour_list, name='full_tour_list'),
    path('full-tours/<str:robot>/', full_tour_by_robot, name='full_tour_by_robot'),

    path("display-video/create/", create_or_update_display_video, name="display-video"),
    path("display-video/list/", list_display_videos, name="display-video-list"),
    path("display-video/delete/<int:pk>/", delete_display_video, name="display-video-delete"),

]