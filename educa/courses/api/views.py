from rest_framework import generics, viewsets
from ..models import Subject, Course
from .serializers import SubjectSerializer, CourseSerializer, CourseWithContentsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, authentication_classes, permission_classes
from .permissions import IsEnrolled


class SubjectListView(generics.ListAPIView):
    '''API View to retrieve the list of subjects.
    
    Attributes:
        queryset: Objects are retrieved using this base queryset.
        serializer_class: Objects are serialized with this class.
    '''
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    '''API View to retrieve detail for specific subject.
    
    Attributes:
        queryset: Objects are retrieved using this base queryset.
        serializer_class: Objects are serialized with this class.
    '''
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset for the Course model. Retrieves the list of objects or 
    detail of a course object.
    '''
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(
        detail=True, # action performed on a specific object
        methods=['post'],
        authentication_classes = [BasicAuthentication],
        permission_classes = [IsAuthenticated]
    )
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)
        return Response({'enrolled':True})

    @action(
        detail=True, # action performed on a specific object
        methods=['get'],
        serializer_class = CourseWithContentsSerializer, # includes rendered course contents
        authentication_classes = [BasicAuthentication],
        permission_classes = [IsAuthenticated, IsEnrolled] # only access to enrolled students
    )
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
