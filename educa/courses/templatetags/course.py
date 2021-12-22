from django import template

register = template.Library()

@register.filter
def model_name(obj):
    '''A model_name template filter that can be applied in templates as
    object|model_name which will retrieve the model name of that 
    object.'''
    try:
        return obj._meta.model_name
    except AttributeError:
        return None