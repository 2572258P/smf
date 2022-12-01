from django import template

register = template.Library()


@register.filter(name='get_val_in_dict')
def get_val_in_dict(dict,key):
    print("dict key - %s"%key)
    print("dict content - ")
    print(dict.get(key))
    return dict.get(key)

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
    print("list content - ")
    print(list)
    if list == None:
        return 'None'
    if index >= 0 or index < list.len():
        return list[index]
    return 'None'
