from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from main.models.models import Question,Answer,UserProfile
from main.views.view_Base import CheckAuth,ShowNotAuthedPage

def loadpage(request,question_type="scq"):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()

    context = {}
    if request.POST.get('delete'):
        deleted = False
        for q in Question.objects.all():
            if request.POST.get('del_'+str(q.pk)):
                Answer.objects.filter(question_id=q.pk).delete()
                q.delete()
                deleted = True
        if deleted:
            context['msg_delete'] = 'Questions have been successfully deleted'
    elif request.POST.get('update_changes'):
        context['msg_dic'] = {}
        for q in Question.objects.all():            
            new_cat = request.POST.get('cat_'+str(q.pk),None)            
            new_pri = request.POST.get('mPri_'+str(q.pk),None)
            new_type = request.POST.get('mType_'+str(q.pk),None)

            if new_pri and new_cat and new_type:
                if new_cat != q.category or new_pri != q.priority or new_type != q.match_type:
                    q.priority = new_pri
                    q.category = new_cat
                    q.match_type = new_type
                    q.save()
                    context['msg_dic'][q.pk] = "Changes have been updated!"
                else:
                    context['msg_dic'][q.pk] = "No change detected"
            
    context['questions'] = Question.objects.all()
    return render(request,'question_editor.html',context)