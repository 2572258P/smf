from django import template

register = template.Library()


@register.filter(name='dict_val')
def dict_val(dict,key):
    return dict[key]

@register.filter(name='get_list_in_dict')
def get_list_in_dict(dict,key):
    return dict[key]

@register.filter(name='is_val_in_list')
def is_val_in_list(list,key):
    for ik in list:
        if ik == key:
            return True
    return False
