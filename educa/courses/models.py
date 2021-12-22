from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.base import Model
from .fields import OrderField
from django.template.loader import render_to_string

class Subject(models.Model):
    '''Model for Subjects.
    
    Fields include:
        title (str): The title of the Subject object.
        slug (slug): The slug of the Subject object. 
    '''
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    '''Model for Courses. A Subject comprises of various Courses
    (i.e. Subject-->Courses).
    
    Fields include:
        owner: Foreign key to the User object related to the Course object.
        subject: Foreign key to the Subject object related to the Course object.
        title (str): The title of the Course object.
        slug (slug): The slug of the Course object.
        overview (str): An overview of the Course object.
        created (datetime obj): Date and time the course was created. Automatically 
            set by due to auto_now_add=True.
        students: Many-to-many relationship between Course and User models to store
            enrolled students.
        modules: One-to-many relationship between the Course and its Modules as a
            list of the primary keys of the Modules.
    '''
    owner = models.ForeignKey(
        to=User,
        related_name='courses_created',
        on_delete=models.CASCADE
        )
    subject = models.ForeignKey(
        to=Subject,
        related_name=('courses'),
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(
        User,
        related_name='courses_joined',
        blank=True
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(models.Model):
    '''Model for Modules. A Course comprises of various Modules (i.e. 
    Subject-->Course-->Modules).
    
    Fields include:
        course: Foreign key to the Course object related to the Module object.
        title (str): The title of the Module object.
        description (str): Optional, a description of the Module object.
        order (int): Sequencial order of the Module.
    '''
    course = models.ForeignKey(
        to=Course,
        related_name='modules',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.title}"


class Content(models.Model):
    '''Model for Contents. Contents make up a Module (i.e. 
    Subject-->Course-->Module-->Contents).
    
    Fields include:
        module: Foreign key to the Module object related to the Content object.
        content_type: Foreign key to the ContentType model.
        object_id: PostiveIntegerField for the primary key of the related object.
        item: GenericForeignKey to the related object by combining the content_type 
            and object_id.
    '''
    module = models.ForeignKey(
        to=Module,
        related_name='contents',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in':(
            'text',
            'video',
            'image',
            'file'
        )}
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    '''ItemBase is a Abstract Model, from which the different content type models (i.e. test, file, video)
    will inheret from. No database will be created for this abstract model, this model only
    provides the common fields for the content models to inherit from.
    
    Fields include:
        owner: Foreign key to the related User object.
        title: Description of the title of the content.
        created: Date, automatically added, of creation of the object.
        updated: Date, autommatically populated, when a change has been made to the object. 
    '''
    owner = models.ForeignKey(
        to=User,
        related_name='%(class)s_related',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        '''Method to return the rendered content as a string.'''
        return render_to_string(
            f'courses/content/{self._meta.model_name}.html',
            {'item':self}
        )
    

# A Module is created for each type of content. The modules will all 
# have common fields which they inherit from the ItemBase abstract Module.
class Text(ItemBase):
    '''Model to store text content. Inherits from the ItemBase model.'''
    content = models.TextField()

class File(ItemBase):
    '''Model to store file content such as PDFs. Inherits from the ItemBase model.'''
    content = models.FileField(upload_to='files')

class Image(ItemBase):
    '''Model to store image files. Inherits from the ItemBase model.'''
    content = models.FileField(upload_to='images')

class Video(ItemBase):
    '''Model to store video content. Inherits from the ItemBase model.
    
    A URLField is used to embed a video URL.
    '''
    url = models.URLField()