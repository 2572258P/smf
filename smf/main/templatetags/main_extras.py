from django import template

register = template.Library()


@register.filter(name='get_val_in_dict')
def get_val_in_dict(dict,key):
    return dict.get(key,'')
    
@register.filter(name='first_in_queryset')
def first_in_queryset(query,id):
    lst = list(query.filter(id=id))
    if len(lst) > 0:
        return lst[0]
    else:
        return ''

@register.filter(name='get_list_in_dict')
def get_list_in_dict(dict,key):
    return dict.get(key)

@register.filter(name='is_val_in_list')
def is_val_in_list(list,key):
    for ik in list:
        if ik == key:
            return True
    return False

@register.filter(name='get_val_in_list')
def get_val_in_list(list,index):
    if list == None:
        return ''
    if index >= 0 and index < len(list):
        return list[index]
    return ''
