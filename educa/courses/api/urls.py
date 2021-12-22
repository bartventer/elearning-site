from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'courses'

# Create and register a Router for the CourseViewSet. 
# This automatically generates URL's for the viewset.
router = routers.DefaultRouter()
router.register('courses', views.CourseViewSet)

urlpatterns = [
    path(
        'subjects/',
        views.SubjectListView.as_view(),
        name='subject_list'
    ),
    path(
        'subjects/<pk>/',
        views.SubjectDetailView.as_view(),
        name='subject_detail'
    ),
    path(
        '',include(router.urls)
    ),
]
