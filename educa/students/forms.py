from django import forms
from courses.models import Course

class CourseEnrollForm(forms.Form):
    '''A course enrollment form for students.'''
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.HiddenInput
    )