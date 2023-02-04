#from django.shortcuts import render
from django.contrib.auth.models import User


from django.http import HttpResponse,Http404,HttpResponseRedirect,JsonResponse
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse


from .models import Question,Choice,LastAccUser,UserProfile,Answer,QuestionVote
from .view_handler_common import CheckAuth,ShowNotAuthedPage,is_ajax
from .view_handler_models import handle_createQuestion
from .view_handler_users import handle_registration,handle_myaccount,handle_mymates
from .view_handler_search import handle_search_result,NLP,handle_sending_message,handle_find_mates
from django.db.models import Q
from django.utils import timezone

def login_requirement(request):
    return render(request,'login_requirement.html',{})




def question_creator(request,question_type="scq"):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()
    profile = UserProfile.objects.filter(user=request.user).first()
    context = handle_createQuestion(request,question_type,profile)
    return render(request,'question_creator.html',context)






def find_mates(request):
    return handle_find_mates(request)

  

def start_searching(request,userId):
        return render(request,'start_searching.html',{"userId":userId})
    
 
def list_result(request,userId):
    if is_ajax(request):        
        return handle_sending_message(request)
    else:
        return handle_search_result(request,userId)



def my_mates(request):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()
    return handle_mymates(request)
