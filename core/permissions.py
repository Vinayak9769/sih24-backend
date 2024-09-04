from .models import Mentor
from rest_framework.permissions import BasePermission

class IsMentor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_mentor