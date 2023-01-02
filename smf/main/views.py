#from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse


from .models import Question,Choice,LastAccUser,UserProfile,Answer#,STF
from .view_handler_models import handle_load,handle_save,handle_createQuestion
from .view_handler_users import handle_registration
from .view_handler_search import handle_search_result,STF


def question_creator(request,question_type="scq"): 
    context = handle_createQuestion(request,question_type) 
    return render(request,'question_creator.html',context)


def question_management(request):
    context = {}
    if request.POST.get('Delete'):
        deleted = False
        for q in Question.objects.all():
            if request.POST.get('del_'+str(q.id)):
                Answer.objects.filter(question_id=q.id).delete()
                q.delete()
                deleted = True
        if deleted:
            context['msg_delete'] = 'Questions have been successfully deleted'
    else:
        context['msg_dic'] = {}
        for q in Question.objects.all():
            if request.POST.get('update'+str(q.id)):
                new_pri = request.POST.get('mPri_'+str(q.id),None)
                new_type = request.POST.get('mType_'+str(q.id),None)
                if new_pri and new_pri != q.priority or new_type and new_type != q.match_type:
                    q.priority = new_pri
                    q.match_type = new_type
                    q.save()
                    context['msg_dic'][q.id] = "Questions have been successfully updated"
                else:
                    context['msg_dic'][q.id] = "Nothing changed"
    
    context['questions'] = Question.objects.all()
    return render(request,'question_management.html',context)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)

                LastAccUser.objects.all().delete()
                lastUser = LastAccUser(lastUser=username)                
                lastUser.save()

                return redirect(reverse('main:dashboard'))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            HttpResponse(f"Invalid login details: {username},{password}")
            return HttpResponse("Invalid login details supplied.")

    return HttpResponse("The request was not POST type")

def user_logout(request):
    logout(request)
    return redirect(reverse('main:dashboard'))

def data_management(request):
    context = {}

    if request.user.is_authenticated:
        context['questions'] = Question.objects.all()
        context['answers'] = {}
        profile = UserProfile.objects.get(user=request.user)
        if 'Find' in request.POST:
            return redirect('main:search_result',userId=request.user.username)
        elif 'Save' in request.POST:
            context['message'] = "Data have successfully saved."        
            handle_save(request,profile)        
        else:
            context['message'] = "Data have successfully loaded."
            
        context['answers'] = handle_load(request,profile)
            
    return render(request,'data_management.html',context)
  

    
 
def search_result(request,userId):
    result = handle_search_result(userId)
    context = { 'search_results' : result }
    return render(request, 'search_results.html',context)

def results(request, question_id):
    question = get_object_or_404(Question,pk=question_id)
    return render(request,'results.html',{'question':question})

def registration(request):
    return render(request,'registration.html', handle_registration(request))


def dashboard(request):
    STF.Init()
    STF.Update()
    context = {}    
    context['questions'] = Question.objects.order_by('pub_date') #sort in ascending order
    user_list = User.objects.all()
    context['users'] = user_list
    context['users_len'] = len(user_list)
    context['answers'] = Answer.objects.order_by('profile')
    context['choices'] = Choice.objects.all()

    sen1 = request.POST.get('sen1','')
    sen2 = request.POST.get('sen2','')
    context['compare_result'] = STF.calculate_single_similarities(sen1,sen2)


    #load the user logged in the lastest time
    last_user = LastAccUser.objects.all()
    if len(last_user) > 0:
        context['last_user'] = last_user[0]

    # test
    print(User.objects.filter(username='admin1').first())
    
    return render(request,'dashboard.html',context)

