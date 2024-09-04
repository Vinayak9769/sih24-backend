from django.urls import path
from .views import register_mentor, update_mentor_profile, verify_email, get_mentor_list, get_mentor_detail, mentor_availability_list, mentor_availability_create
urlpatterns = [
    path('register/mentor/', register_mentor),
    path('update/mentor/', update_mentor_profile),
    path('verify-email/<uuid:token>/', verify_email),
    path('mentors/', get_mentor_list),
    path('mentor/<int:mentor_id>/', get_mentor_detail),
    path('<int:id>/slots/', mentor_availability_list, name='mentor_availability_list_create'),
    path('slots/', mentor_availability_create, name='mentor_availability_list_create'),

]
