from django.urls import path
from education.views import *

urlpatterns = [
    path('students/create/', create_student, name='create-student'),
    path('students/list/<int:user_id>/', list_students, name='list_students'),
    path('students/edit/<int:student_id>/', edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', delete_student, name='delete_student'),

    path('subjects/create/', create_subject, name='create_subject'),
    path('subjects/list/<int:user_id>/', list_subjects_by_user, name='list_subjects_by_user'),
    path('subjects/update/<int:subject_id>/', update_subject, name='update_subject'),
    path('subjects/delete/<int:subject_id>/', delete_subject, name='delete_subject'),

    path('upload-pdf/', upload_pdf_document, name='upload-pdf'),
    path('pdfs/list/<int:subject_id>/', pdf_list_by_subject, name='pdf-list-by-subject'),
    path('pdf/edit/<int:pk>/', edit_pdf_document, name='edit-pdf-document'),
    path('pdf/delete/<int:pk>/', delete_pdf_document, name='delete-pdf-document'),

    path('lastmodule/', lastmodule_replace_view, name='lastmodule-replace'),
    path('lastmodule/detail/', lastmodule_list_view, name='lastmodule-list'),
]