from django.urls import path
from appointment.views import *

urlpatterns = [ 
    path('persons/list/', person_list, name='person_list'),

    path('appointments/create/', create_appointment, name='create_appointment'),
    path('appointments/list/', list_appointments, name='list_appointments'),
    path('appointments/detail/<int:pk>/', appointment_detail, name='appointment_detail'),

]