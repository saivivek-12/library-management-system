from rest_framework.permissions import BasePermission, SAFE_METHODS

class AdminWriteOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return hasattr(user, 'student') and user.student.is_active

class IsLibrarian(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return hasattr(user, 'student') and user.student.role in ['LIBRARIAN', 'SUPER_ADMIN'] and user.student.is_active

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return hasattr(user, 'student') and user.student.role == 'SUPER_ADMIN' and user.student.is_active