from django import template

register = template.Library()
@register.filter(name='dict_val')
def dict_val(dict,key):
    return dict[key]
    
