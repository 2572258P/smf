from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils import timezone

from main.views.view_Base import CheckAuth,ShowNotAuthedPage
from main.models.models import Question,Answer,UserProfile


def loadpage(request,question_type="scq"):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()
    profile = UserProfile.objects.filter(user=request.user).first()

    scq_text = request.POST.get('scq_text','')
    mcq_text = request.POST.get('mcq_text','')
    tbq_text = request.POST.get('tbq_text','')
    category = request.POST.get('category','')
    priority = request.POST.get('mPri','')
    desc = request.POST.get('desc')
    match_type = request.POST.get('mType','smt') #default value 'smt'

    scq_choice_num = range(1,21)
    mcq_choice_num = range(1,21)
    message = ''
    if scq_text == '' and mcq_text == '' and tbq_text == '':
        if question_type == 'tbq':
            message = 'Text-Based Question - Enter your question'
        elif question_type == 'scq':            
            message = 'Single-Choice Question - Enter a question and choices.'
        elif question_type == 'mcq':
            message = 'Multiple-Choice Question - Enter a question and choices.'        
    else:
        try:            
            if len(scq_text) > 0:
                q = Question(approved=profile.admin,type="scq",ctrl_type='radio',title=scq_text,pub_date=timezone.now(),priority = priority,match_type = match_type,category=category,desc=desc)
                q.save()
                for i in scq_choice_num:
                    choice_text = request.POST.get("scq_c%i"%i,'')                
                    if choice_text != '':
                        q.choice_set.create(choice_text=choice_text)
            if len(mcq_text) > 0:
                q = Question(approved=profile.admin,type="mcq",ctrl_type='checkbox',title=mcq_text,pub_date=timezone.now(),priority = priority,match_type = match_type,category=category,desc=desc)
                q.save()
                for i in mcq_choice_num:
                    choice_text = request.POST.get("mcq_c%i"%i,'')
                    if choice_text != '':
                        q.choice_set.create(choice_text=choice_text)
            if len(tbq_text) > 0:                
                q = Question(approved=profile.admin,type="tbq",ctrl_type='textarea',title=tbq_text,desc=desc,pub_date=timezone.now(),priority = priority,match_type = match_type,category=category)
                q.save()
            message = 'New question has been successfully created.'

        except Exception as inst:
            print(inst)
        
    context = {'message':message,'scq_choice_num':scq_choice_num,'mcq_choice_num':mcq_choice_num,'selectedType':question_type}
    return render(request,'question_submit.html',context)