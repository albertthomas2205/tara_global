from django.urls import path
from hospital.views import *

urlpatterns = [
    path('patients/create/', create_patient, name='create-patient'),
    path('patients/list/<int:user_id>/', list_patients_by_user, name='list_patients_by_user'),
    path('patients/edit/<int:pk>/', edit_patient, name='edit_patient'),
    path('patients/detail/<int:pk>/', patient_detail, name='patient_detail'),
    path('patients/delete/<int:pk>/', delete_patient, name='delete_patient'),


    path('create/room/', create_room, name='create_room'),
    path('list/rooms/<str:robot>/', list_rooms_by_robot, name='list_rooms_by_robot'),
    path('api/rooms/delete_by_robot/<str:robot_id>/', delete_rooms_by_robot, name='delete-rooms-by-robot'),

    

    path('assign-patient/<int:user_id>/', assign_patient_to_room, name='assign-patient'),
    path('assignment/list/<int:user_id>/', list_patient_room_assignments, name='assignment-list'),
    path('assignment/update/<int:pk>/', update_patient_room_assignment,name='assignment-update'),
    path('assignment/detail/<int:pk>/', get_patient_room_assignment_detail,name='assignment-detail'),
    path('assignment/delete/<int:pk>/', delete_patient_room_assignment,name='assignment_delete'),

    path('assignments/room/edit-text/<str:room_number>/', update_assignment_text_by_room, name='edit_assignment_text_by_room'),
    path('assignment/room/detail/<str:room_number>/', assignment_detail_by_room_number, name='assignment_detail_by_room_number'),

]