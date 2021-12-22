from rest_framework.permissions import BasePermission

class IsEnrolled(BasePermission):
    '''Custom permission class for students to access contents of the
    courses they are enrolled in.
    '''
    def has_object_permission(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()