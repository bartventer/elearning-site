from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView

class StudentRegistrationView(CreateView):
    '''View for users to register on the site.'''
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        '''Returns an HTTP reponse if valid form data has been posted.
        A user is logged in after they have successfully registered.
        '''
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    '''View for students to enroll on courses.'''
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        '''Override the form_valid method, to ensure that upon
        successfull submission of the form data, the student is
        added to the Course model.'''
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)
    
    def get_success_url(self):
        '''Returns the redirected url after the user has been enrolled.'''
        return reverse_lazy(
            'student_course_detail',
            args=[self.course.id]
        )


class StudentCourseListView(LoginRequiredMixin, ListView):
    '''View to display enrolled courses for a user.'''
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        '''Override the get_queryset() method to filter the Course
        model for those courses the student is enrolled in.
        '''
        qs =  super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(DetailView):
    '''View to display the detail of a specific course.'''
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        '''Override the get_queryset() method to only return those
        courses for which the user is registered.'''
        qs =  super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        '''Override get_context_data() method in order to set a
        specific module object in the context, if the module_id URL
        paramater was provided, otherwise default to the first module 
        of the course.'''
        context =  super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                id = self.kwargs['module_id']
            )
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context


