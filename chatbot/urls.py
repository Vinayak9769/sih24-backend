from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_view, name='generate_dog_recommendation'),
]
