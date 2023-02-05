from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.models.models import Question,Answer,UserProfile
from .view_Base import CheckAuth,ShowNotAuthedPage,is_ajax
from ..modules.module_search import CategoryInfo
from ..modules.module_common import GetCategoryLabel

def get_per_ans(mp):
    apv_qs = Question.objects.all().exclude(approved=False) # Get all questions except unapproved Qs
    #Count I have answered
    total_qs_count = apv_qs.count() #Getting the count I have answered
    my_anss = Answer.objects.filter(profile=mp)
    ass_count = 0
    duplicated = {}
    for ans in my_anss:
        #check whether the answer is duplicated in the same questions, which can happen in MCQ-type questions.
        if Question.objects.filter(pk=ans.question_id).first() and ans.question_id not in duplicated:
            duplicated[ans.question_id] = ans.question_id
            ass_count += 1
    return int(ass_count / total_qs_count * 100) if total_qs_count > 0 else 0

def get_cat_infos(mp):
    apv_qs = Question.objects.all().exclude(approved=False) # Get all questions except unapproved Qs    
    total_qs_count = apv_qs.count() #Getting the count I have answered
    my_anss = Answer.objects.filter(profile=mp)
    ass_count = 0
    duplicated = {}
    cat_info_objs = {}
    cat_info_objs['cc'] = CategoryInfo('cc')
    cat_info_objs['cd'] = CategoryInfo('cd')
    cat_info_objs['cb'] = CategoryInfo('cb')

    for ans in my_anss:
        #check whether the answer is duplicated in the same questions, which can happen in MCQ-type questions.
        q = Question.objects.filter(pk=ans.question_id).first()
        if q and ans.question_id not in duplicated:            
            duplicated[ans.question_id] = ans.question_id
            ass_count += 1
            if q.category not in cat_info_objs:
                cat_info_objs[q.category] = CategoryInfo(q.category)
            cat_info_objs[q.category].totalScore = apv_qs.filter(category=q.category).count()
            cat_info_objs[q.category].addPoint(1)
    
    cat_infos = {}
    for k,ci in cat_info_objs.items():
        cat_infos[ GetCategoryLabel(ci.label) ] = ci.per
    
    return cat_infos

def load(request,profile):
    answers = {}

    if profile:
        for ans in Answer.objects.filter(profile=profile):            
            if ans.question_id not in answers:
                answers[ans.question_id] = []
            if ans.choice_id != -1:
                answers[ans.question_id].append(ans.choice_id)
            answers[ans.question_id].append(ans.answer_text)
    return answers
    
def save(request,profile):
    for q in Question.objects.all().filter(approved=True):
        anss = Answer.objects.filter(profile=profile,question_id=q.pk)
        anss.delete()
        if q.type == 'scq' or q.type == 'mcq':
            c_id = "choice" + str(q.pk)
            if q.type == 'scq' and request.POST.get(c_id):
                a = Answer(profile=profile,question_id=q.pk,choice_id=request.POST.get(c_id,-1))
                a.save()
            elif q.type == 'mcq':
                for ans in request.POST.getlist(c_id):                    
                    a = Answer(profile=profile,question_id=q.pk,choice_id=ans)
                    a.save()
        elif q.type == 'tbq':
            text_ans = request.POST["text_ans%i"%q.pk]
            if len(text_ans) > 0:
                a = Answer(profile=profile,question_id=q.pk,answer_text=text_ans)
                a.save()

def loadpage(request):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()

    apv_qs = Question.objects.all().exclude(approved=False) # Get all questions except unapproved Qs
    mp = UserProfile.objects.filter(user=request.user).first()
    if not mp:
        return HttpResponse("{} User Profile Does not Exist".format(request.user))
    #Total count of approved quetions

    if is_ajax(request): #Saving
        mp = UserProfile.objects.filter(user=request.user).first()
        save(request,mp)

        cat_infos = get_cat_infos(mp)
        label = GetCategoryLabel('cd')
        if label in cat_infos and cat_infos[label] > 0:
            cat_infos[label] = 100
        
        data = {"per_ans":get_per_ans(mp), "cat_infos":cat_infos }
        
        return JsonResponse(data)
    else: #Only for loading
        context = {}
        #labelling for categories    
        category_pair = {"cc":GetCategoryLabel('cc'),"cd":GetCategoryLabel('cd'),\
            "cb":GetCategoryLabel('cb'),"cu":"Registered by users"}
        context['cat_qs'] = {}
        for k,v in category_pair.items():
            context['cat_qs'][k] = apv_qs.filter(category=k)
        context['category_pair'] = category_pair
        context['questions'] = apv_qs
        context['answers'] = {}        
        context['message'] = "Data have been successfully loaded."                
        context['answers'] = load(request,mp)
        context['per_ans'] = get_per_ans(mp)
        cat_infos = get_cat_infos(mp)

        label = GetCategoryLabel('cd')
        if label in cat_infos and cat_infos[label] > 0:
            cat_infos[label] = 100
        print(cat_infos)
        context['cat_infos'] = cat_infos
        return render(request,'find_mates.html',context)