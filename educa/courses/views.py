from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from . models import Module, Content
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from .models import Subject
from django.views.generic.detail import DetailView
from students.forms import CourseEnrollForm
from django.core.cache import cache


#Mixins
class OwnerMixin(object):
    '''Mixin to be used with ListView, CreateView, UpdateView and DeleteView.
    
    Overrides the get_queryset() method to filter objects by the owner attribute
    to retrieve objects that belong to the current user (request.user).

    This Mixin can be used with any of the above mentioned views that interact
    with any model that contains an owner attribute.
    '''
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    '''Mixin to be used with ListView, CreateView, UpdateView and DeleteView.
    
    Implements the form_valid() method, used by views using ModelFormMixin (views
    with forms or model forms such as CreateView and UpdateView).
    
    form_valid() is executed when the submitted form is valid.

    Overrides the defualt behaviour of redirecting the user to the success_url, by
    automatically setting the current user in the owner attribute of the object
    being saved.
    '''
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    '''Class that inherits from OwnerMixin, LoginRequiredMixin, and
    PermissionRequiredMixin, providing the following attributes for 
    child views:

        model: 
            The model that is used for QuerySets; used by all views.
        fields:
            Fields of the model to build the model form of the
            CreateView and UpdateView views.
        success_url:
            CreateView, UpdateView, and DeleteView use this attribute
            to redirect the user after successful submission of the 
            form or deletion of the object.
    '''
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    '''Inhertis from OwnerCourseMixin and OwnerEditMixin,and defines a 
    template_name attribute for a template to be used for the 
    CreateView and UpdateView.
    '''
    template_name = 'courses/manage/course/form.html'


#Views of the content management system for instructors/course creators
class ManageCourseListView(OwnerCourseMixin, ListView):
    '''Lists the courses created by the user. 
    
    Defines a template_name attribute, to list courses for a template,
    and a permission_required attribute, to validate that the user
    accessing the view has the specified permission.
    '''
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    '''Uses a model form to create a new Course object. 
    
    Uses fields defined in the OwnerCourseMixin for building a model 
    form, and subclasses CreateView. 
    
    The template defined in OwnerCourseEditMixin will be used.
    
    Defines a permission_required attribute, to validate that the user
    accessing the view has the specified permission.
    '''
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    '''Will allow editing of an existing object.
    
    Uses fields defined in the OwnerCourseMixin for building a model 
    form, and subclasses UpdateView. 
    
    The template defined in OwnerCourseEditMixin will be used.
    
    Defines a permission_required attribute, to validate that the user
    accessing the view has the specified permission.
    '''
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    '''Will allow deletion of an existing object.
    
    This class inherits from OwnerCourseMixin and the generic
    DeleteView.
    
    Defines a template_name attribute, for a template to confirm
    deletion of a course, and a permission_required attribute, to 
    validate that the user accessing the view has the specified 
    permission.
    '''
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    '''View to handle the formset for adding, updating, and deleting
    modules for a specific course.
    '''
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        '''Returns a ModelFormSet for the given data.'''
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        '''Retrieves the Course object based on the given paramaters
        and delegates it to the get() or post() methods that match
        the HTTP request method (either GET or POST).
        '''
        self.course = get_object_or_404(
            Course,
            id=pk,
            owner=request.user
        )
        return super().dispatch(request, pk)
    
    def get(self, request, *args, **kwargs):
        '''Renders an empty ModelFormSet formset together with the
        current Course object to the template.
        '''
        formset = self.get_formset()
        return self.render_to_response({'course':self.course,'formset':formset})
    
    def post(self, request, *args, **kwargs):
        '''Renders a ModelFormSet formset based on the submitted data.

        If all forms in the formset are valid, the updates are applied
        to the model, and the user is redirected to the 
        manage_course_list URL.

        The template is rendered to display any errors, if the formset
        is not valid.
        '''
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course':self.course, 'formset':formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    '''Class that allows creating and updating different model's content.'''
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        '''Returns the class for the given model_name. Returns None if
        the model_name isn't valid.
        '''
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None
    
    def get_form(self, model, *args, **kwargs):
        '''Returns a dynamic form which can be used for Text, Video,
        Image, and Field models.
        '''
        Form = modelform_factory(
            model,
            exclude=[
                'owner',
                'order',
                'created',
                'updated'
            ]
        )
        return Form(*args, **kwargs)
    
    def dispatch(self, request, module_id, model_name, id=None):
        '''Returns an HTTP response. Based on the given paramaters, it
        stores as class attributes the corresponding module, model and
        content object.

        Paramaters:
            module_id:
                The ID of the given module that the will be associated
                with.
            model_name:
                Model name of the content to update/create.
            id:
                ID of the object being updated. To create new objects
                is None.
        '''
        self.module = get_object_or_404(
            Module,
            id=module_id,
            course__owner=request.user
        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(
                self.model,
                id=id,
                owner=request.user
            )
        return super().dispatch(request, module_id, model_name, id)
    
    def get(self, request, module_id, model_name, id=None):
        '''Returns an HTTP response when a GET request is received.'''
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({
            'form':form,
            'object':self.obj
        })

    def post(self, request, module_id, model_name, id=None):
        '''Returns an HTTP response when a POST request is received.'''
        form = self.get_form(
            self.model,
            instance = self.obj,
            data = request.POST,
            files = request.FILES
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(
                    module = self.module,
                    item=obj
                )
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({
            'form':form,
            'object':self.obj
        })

class ContentDeleteView(View):
    '''View for deleting content.'''

    def post(self, request, id):
        '''Returns an HTTP response redirect when a POST request is 
        received.
        
        Based on the given id, this method retrieves the Content 
        object, then deletes the related Text, Video, Image or File 
        object. Then deletes the Content object, and redirects the user
        to the list of other contents for the module.
        '''
        content = get_object_or_404(
            Content,
            id=id,
            module__course__owner=request.user
        )
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    '''View to display all modules and their contents.'''

    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)

        return self.render_to_response({'module': module}) 


class ModuleOrderView(CsrfExemptMixin,
                      JsonRequestResponseMixin,
                      View):
    '''View to receive the new order of module IDs encoded in JSON.'''
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                   course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin,
                       JsonRequestResponseMixin,
                       View):
    '''View to receive the new order of content IDs of a module encoded
    in JSON.'''
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                       module__course__owner=request.user) \
                       .update(order=order)
        return self.render_json_response({'saved': 'OK'})


#Public views for displaying course information
class CourseListView(TemplateResponseMixin, View):
    '''View to display the course catalog.'''

    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        '''Returns an HTTP response, by rendering the retrieved objects
        to a template.'''
        # Retrieve all subjects, and the total number of courses
        # for each subject. And cache the queryset in memory.
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(
                total_courses = Count('courses')
            )
            cache.set('all_subjects', subjects)
        # Retrieve all available courses, and the total number of
        # modules for each course.
        all_courses = Course.objects.annotate(
            total_modules=Count('modules')
        )
        # If Subject slug provided, retrieve that subject and limit 
        # courses to those that relate to the given subject.
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject = subject)
                cache.set(key,courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response({
            'subjects':subjects,
            'subject':subject,
            'courses':courses
        })

        
class CourseDetailView(DetailView):
    '''Detail view to display the overview for a single course.'''
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        '''Override get_context_data to include the enrollment form
        in the context being rendered for the template.
        '''
        context =  super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
            initial={'course':self.object}
        )
        return context



