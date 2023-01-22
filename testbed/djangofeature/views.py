from django.shortcuts import render

class cls:
    def __init__(self, name, age):
        self.name = name
        self.age = age


# Create your views here.
def index(request):
    context = {}
    context['objs'] = [cls("jay",26),cls("park",40)]
    return render(request,'df_index.html',context)
