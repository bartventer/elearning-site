from rest_framework import serializers
from ..models import Subject, Course, Module, Content

class SubjectSerializer(serializers.ModelSerializer):
    '''Serializer for the Subject Model.'''
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']


class ModuleSerializer(serializers.ModelSerializer):
    '''Serializer for the Module Model.'''
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']


class CourseSerializer(serializers.ModelSerializer):
    '''Serializer for the Course Model. Includes a custom field for 
    Modules to render the list of Module objects instead of their primary
    keys.'''

    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug',
        'overview', 'created','owner', 'modules']


class ItemRelatedField(serializers.RelatedField):
    '''Custom Field for Content Item generic foreign key.'''
    def to_representation(self, value):
        return value.render()


class ContentSerializer(serializers.ModelSerializer):
    '''Serializer for the Content Model.'''
    item = ItemRelatedField(read_only = True)

    class Meta:
        model = Content
        fields = ['order', 'item']


class ModuleWithContentsSerializer(serializers.ModelSerializer):
    '''Alternative serializer for the Module Model, inclusive of its
    Contents.'''
    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ['order', 'title', 'description', 'contents']


class CourseWithContentsSerializer(serializers.ModelSerializer):
    '''Extend serializer for the Course Model, inclusive of Custom
    Serliazed Content for the Modules.'''
    modules = ModuleWithContentsSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug',
        'overview', 'created','owner', 'modules']