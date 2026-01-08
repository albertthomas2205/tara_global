from django.urls import path
from police.views import *

urlpatterns = [
    path('complaints/create/', create_complaint, name='create_complaint'),
    path('complaints/list/', get_user_complaints_paginated, name='list_complaints_by_user'),
    path('complaints/edit/<str:case_id>/', update_complaint_by_case_id, name='update_complaint'),
    path('last-case-id/', get_last_case_id_by_user, name='last-case-id-by-user'),
    path('complaint/detail/<str:case_id>/', complaint_detail, name='complaint-detail'),

    path('speak/create/', create_speak, name='create-speak'),
    path('speak/list/', list_speak, name='list-speak'),

]