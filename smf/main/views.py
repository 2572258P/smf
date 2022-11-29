#from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse

from .models import Question,Choice,LastAccUser,UserProfile
from .handler_models import handle_load,handle_save
from .handler_users import handle_registration

"""
Show last user when
1.Entry 2.Load 
Save last user when
1. Save 2. Load only when succeeeded

"""

def data_management(request):
    
    context = {}

    context['questions'] = Question.objects.all()
    print('entry')
    
    posted_name = request.POST.get('userId','')
    print("posted name %s" % posted_name)

    if posted_name != '':
        try:
            foundUser = User.objects.get(username=posted_name)
            profile = UserProfile.objects.get(user=foundUser)
        except:
            if posted_name != '':
                context['message'] = "The user does not exist"
        else:
            if 'Find' in request.POST:
                print('find')
                return redirect('main:search_result')
            elif 'Load' in request.POST:
                print("Load - %s" % posted_name)
                context['message'] = "Data have successfully loaded."
                context['last_user'] = request.POST['userId']
                context['answers'] = handle_load(request,profile)
            elif 'Save' in request.POST:
                print("Save - %s" % foundUser)
                context['message'] = "Data have successfully saved."        
                handle_save(request,profile)

            lastUser = LastAccUser.objects.first()
            lastUser.lastUser = request.POST['userId']
            lastUser.save()        
            context['last_user'] = request.POST['userId']
    else:        
        context['last_user'] = LastAccUser.objects.first()

    return render(request,'data_management.html',context)    
 
def search_reslt(request):
    return HttpResponse("Show Results")

def results(request, question_id):
    question = get_object_or_404(Question,pk=question_id)
    return render(request,'results.html',{'question':question})

def registration(request):
    return render(request,'registration.html', handle_registration(request))

def index(request):
    latest_question_list = Question.objects.order_by('pub_date') #sort in ascending order
    output = '<br>'.join([q.question_text for q in latest_question_list])
    template = loader.get_template('index.html')
    context = {'latest_question_list' : latest_question_list}
    #return HttpResponse(template.render(context,request))
    return render(request,'index.html',context)

#----- Code snippets -----
def vote(request, question_id):
    question = get_object_or_404(Question,pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        
    except (KeyError,Choice.DoesNotExist):
        return render(request,'detail.html',{'question':question,"error_message": "You didn't select a choice.",})
    else:
        print(request.POST['choice'])
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('main:results', args=(question.id,)))


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except:
        raise Http404("Question does not exist")
           
    return render(request,'detail.html',{'question':question})

def test(request):
    return render(request,'registration.html',{})    