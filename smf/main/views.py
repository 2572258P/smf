#from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.utils import timezone

from .models import Question,Choice,LastAccUser,UserProfile,Answer
from .view_handler_models import handle_load,handle_save
from .view_handler_users import handle_registration

"""
Show last user when
1.Entry 2.Load 
Save last user when
1. Save 2. Load only when succeeeded

"""

def question_creator(request):
    scq_text = request.POST.get('scq_text','')
    mcq_text = request.POST.get('mcq_text','')
    tbq_text = request.POST.get('tbq_text','')
    scq_choice_num = range(1,11)
    mcq_choice_num = range(1,11)
    message = ''
    if scq_text == '' and mcq_text == '' and tbq_text == '':
        message = 'Enter questions and choices with types at least one'
    else:
        if scq_text != '':
            q = Question(type="scq",ctrl_type='radio',question_text=scq_text,pub_date=timezone.now())        
            q.save()
            for i in scq_choice_num:
                choice_text = request.POST.get("scq_c%i"%i,'')
                if choice_text != '':
                    q.choice_set.create(choice_text=choice_text)
        if mcq_text != '':
            q = Question(type="mcq",ctrl_type='checkbox',question_text=mcq_text,pub_date=timezone.now())        
            q.save()
            for i in mcq_choice_num:
                choice_text = request.POST.get("mcq_c%i"%i,'')
                print(choice_text)
                if choice_text != '':
                    q.choice_set.create(choice_text=choice_text)
        if tbq_text != '':
            q = Question(type="tbq",ctrl_type='textarea',question_text=tbq_text,pub_date=timezone.now())        
            q.save()
    return render(request,'question_creator.html',{'message':message,'scq_choice_num':scq_choice_num,'mcq_choice_num':mcq_choice_num})

def data_management(request):    
    context = {}
    context['questions'] = Question.objects.all()
    print('entry')
    context['answers'] = {}
    
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

            lastUser = LastAccUser.objects.get_or_create(lastUser=posted_name)[0]           
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

def dashboard(request):    
    context = {}
    
    context['questions'] = Question.objects.order_by('pub_date') #sort in ascending order
    user_list = User.objects.all()
    context['users'] = user_list
    context['users_len'] = len(user_list)
    context['answers'] = Answer.objects.order_by('profile')
    context['choices'] = Choice.objects.all()

    return render(request,'dashboard.html',context)


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