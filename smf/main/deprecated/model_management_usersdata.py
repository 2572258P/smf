from django.shortcuts import render
from django.http import HttpResponse

from .models import Answer,Question
from .views_commons import CheckAuth,ShowNotAuthedPage


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

def setting(request):
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
        data = {"per_ans":get_per_ans(mp)}
        return JsonResponse(data)
    else: #Only for loading
        context = {}
        #labelling for categories    
        category_pair = {"cc":"Common Questions","cd":"Details","cb":"Psychology","cu":"Registered by users"}        
        context['cat_qs'] = {}
        for k,v in category_pair.items():
            context['cat_qs'][k] = apv_qs.filter(category=k)
        context['category_pair'] = category_pair
        context['questions'] = apv_qs
        context['answers'] = {}        
        context['message'] = "Data have been successfully loaded."                
        context['answers'] = load(request,mp)
        context['per_ans'] = get_per_ans(mp)
        return render(request,'find_mates.html',context)



