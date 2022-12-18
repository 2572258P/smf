#from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse


from .models import Question,Choice,LastAccUser,UserProfile,Answer,STF
from .view_handler_models import handle_load,handle_save,handle_createQuestion
from .view_handler_users import handle_registration
from .view_handler_search import handle_search_result


def question_creator(request,question_type="scq"): 
    context = handle_createQuestion(request,question_type) 
    return render(request,'question_creator.html',context)

def data_management(request):    
    context = {}
    context['questions'] = Question.objects.all()
    context['answers'] = {}
    
    posted_name = request.POST.get('userId','')

    if posted_name != '':
        try:
            foundUser = User.objects.get(username=posted_name)
            profile = UserProfile.objects.get(user=foundUser)
        except:
            if posted_name != '':
                context['message'] = "The user does not exist"
        else:
            if 'Find' in request.POST:
                return redirect('main:search_result',userId=posted_name)
            elif 'Load' in request.POST:
                context['message'] = "Data have successfully loaded."
                context['last_user'] = request.POST['userId']
                context['answers'] = handle_load(request,profile)
            elif 'Save' in request.POST:
                context['message'] = "Data have successfully saved."        
                handle_save(request,profile)
            
            LastAccUser.objects.all().delete()
            lastUser = LastAccUser.objects.get_or_create(lastUser=posted_name)[0]
            lastUser.lastUser = request.POST['userId']
            lastUser.save()
            context['last_user'] = request.POST['userId']
    else:        
        context['last_user'] = LastAccUser.objects.first()

    return render(request,'data_management.html',context)
 
def search_result(request,userId):
    print("----- UserId %s"%userId)
    result = handle_search_result(userId)
    for r in result:
        print(r.percent)
    context = { 'search_results' : result }
    return render(request, 'search_results.html',context)

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

    sen1 = request.POST.get('sen1','')
    sen2 = request.POST.get('sen2','')
    context['compare_result'] = sen2
    if sen1 != '' and sen2 != '':
        context['compare_result'] = STF.calculate_single_similarities(sen1,sen2)
    else:
        context['compare_result'] = ''

    return render(request,'dashboard.html',context)


#----- Code snippets -----
def vote(request, question_id):
    question = get_object_or_404(Question,pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        
    except (KeyError,Choice.DoesNotExist):
        return render(request,'detail.html',{'question':question,"error_message": "You didn't select a choice.",})
    else:
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
    print(STF.scores[0][2])
    return HttpResponse("This is test page!")