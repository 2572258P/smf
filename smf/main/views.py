#from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

from django.http import HttpResponse,Http404,HttpResponseRedirect,JsonResponse
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse


from .models import Question,Choice,LastAccUser,UserProfile,Answer,QuestionVote#,STF
from .view_handler_common import CheckAuth,ShowNotAuthedPage,is_ajax
from .view_handler_models import handle_load,handle_save,handle_createQuestion
from .view_handler_users import handle_registration,handle_myaccount
from .view_handler_search import handle_search_result,STF
from django.db.models import Q

def login_requirement(request):
    return render(request,'login_requirement.html',{})



def dashboard(request):
    STF.Init()
    STF.Update()
    context = {}    
    context['questions'] = Question.objects.order_by('pub_date').exclude(approved=False) #sort in ascending order
    
    dict_dqs = {}
    dqs = Question.objects.all().exclude(approved=True)
    for dq in dqs:
        up = QuestionVote.objects.filter(question = dq).filter(vote_val__gt = 0).count()
        down = QuestionVote.objects.filter(question = dq).filter(vote_val__lt = 0).count()
        dict_dqs[dq.pk] = up - down
    sort_dqs = dict(sorted(dict_dqs.items(), key=lambda item: item[1],reverse=True))
    context['draft_questions'] = []
    for k,v in sort_dqs.items():
        context['draft_questions'].append(Question.objects.get(pk=k))
    

    profile_list = UserProfile.objects.all()
    context['profiles'] = profile_list
    context['profile_len'] = profile_list.count()
    context['answers'] = Answer.objects.order_by('profile')
    context['choices'] = Choice.objects.all()

    sen1 = request.POST.get('sen1','')
    sen2 = request.POST.get('sen2','')
    context['compare_result'] = STF.calculate_single_similarities(sen1,sen2)
    
    #load the user logged in the lastest time
    last_user = LastAccUser.objects.all()
    context['last_user'] = last_user[0] if last_user.count() > 0 else ""
  

    if is_ajax(request): # Handling from ajax request
        response = {}
        qid = request.POST.get('qid', None)
        q = Question.objects.filter(pk=qid).first()
        qv = QuestionVote.objects.filter(username=request.user.username,question=q).first()
        new_val = int(request.POST.get('vote'))

        #Calculating vote count value to apply to Model
        if qv is None: #At first time of attempting restration
            prev_val = 0
            response['msg'] = "You have voted to" + ("up" if new_val > 0 else "down") + "."
            qv = QuestionVote(username=request.user.username,question=q)
        else:
            prev_val = qv.vote_val
            
            if prev_val + new_val == 0: #Opposite Vote
                response['msg'] = "You have voted to " + ("up" if new_val > 0 else "down") + "."
                new_val = new_val * 2
            elif prev_val + new_val > 1 or prev_val + new_val < -1: #Up or Down vote again
                new_val = -prev_val
                response['msg'] = "You vote has been cancelled."
            else:
                response['msg'] = "You have voted to " + ("up" if new_val > 0 else "down") + "."                
        result_val = prev_val + new_val
        qv.vote_val = result_val            
        qv.save()
        print(result_val)
        response['result_val'] = result_val

        vote_count_up = QuestionVote.objects.filter(question=q).filter(vote_val__gt=0).count()
        vote_count_down = QuestionVote.objects.filter(question=q).filter(vote_val__lt=0).count()
        
        response['result_up'] = vote_count_up
        response['result_down'] = vote_count_down
        
        alluserCount = UserProfile.objects.all().exclude(admin=True).count()
        voteCount = QuestionVote.objects.filter(question=qid).filter(vote_val__gt=0).count();

        if voteCount > alluserCount/2:
            q.approved = True
            q.save()

        return JsonResponse(response)
    else:
        context['up_vote_count'] = {}
        context['down_vote_count'] = {}
        context['my_vote'] = {}
        
        for dq in Question.objects.all().exclude(approved=True):
            up_query = Q(question=dq)
            context['up_vote_count'][dq.pk] = QuestionVote.objects.filter(question=dq,vote_val__gt=0).count()
            context['down_vote_count'][dq.pk] = QuestionVote.objects.filter(question=dq,vote_val__lt=0).count()
            votedQ = QuestionVote.objects.filter(question=dq,username=request.user.username).first()
            
            context['my_vote'][dq.pk] = votedQ.vote_val if votedQ else 0
        print(context['my_vote'])
        return render(request,'dashboard.html',context)



def question_creator(request,question_type="scq"):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()
    profile = UserProfile.objects.filter(user=request.user).first()
    context = handle_createQuestion(request,question_type,profile)
    return render(request,'question_creator.html',context)


def question_management(request):    
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()
    if request.user.is_authenticated is False:
        return HttpResponse("The page requires log-in")

    context = {}
    if request.POST.get('delete'):
        deleted = False
        for q in Question.objects.all():
            if request.POST.get('del_'+str(q.id)):
                Answer.objects.filter(question_id=q.id).delete()
                q.delete()
                deleted = True
        if deleted:
            context['msg_delete'] = 'Questions have been successfully deleted'
    elif request.POST.get('update_changes'):
        
        context['msg_dic'] = {}
        for q in Question.objects.all():            
            new_pri = request.POST.get('mPri_'+str(q.id),None)
            new_type = request.POST.get('mType_'+str(q.id),None)
            if new_pri and new_pri != q.priority or new_type and new_type != q.match_type:
                q.priority = new_pri
                q.match_type = new_type
                q.save()
                context['msg_dic'][q.id] = "Changes have been updated!"
            else:
                context['msg_dic'][q.id] = "No change detected"

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
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()
    context = {}

    if request.user.is_authenticated:
        context['questions'] = Question.objects.all().exclude(approved=False)
        context['answers'] = {}
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            if 'Find' in request.POST:
                return redirect('main:search_result',userId=request.user.username)
            elif 'Save' in request.POST:
                context['message'] = "Data have been successfully saved."        
                handle_save(request,profile)        
            else:
                context['message'] = "Data have been successfully loaded."
                
            context['answers'] = handle_load(request,profile)                
            return render(request,'data_management.html',context)
        else:
            return HttpResponse("{} User Profile Does not Exist".format(request.user))
  

    
 
def search_result(request,userId):
    result = handle_search_result(userId)
    context = { 'search_results' : result }
    return render(request, 'search_results.html',context)

def results(request, question_id):
    question = get_object_or_404(Question,pk=question_id)
    return render(request,'results.html',{'question':question})

def registration(request):
    return handle_registration(request)

def my_account(request):
    return handle_myaccount(request)