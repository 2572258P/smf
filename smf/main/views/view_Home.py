from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q

from .view_Base import is_ajax
from main.models.models import Question,Answer,UserProfile,Choice,QuestionVote
from main.modules.module_NLP import NLP
from django.core.mail import send_mail


def loadpage(request):
    NLP.Init()
    NLP.Update()
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
    comp_result = NLP.calculate_single_similarities(sen1,sen2)    
    context['compare_result'] = comp_result

    target_count = round(UserProfile.objects.all().count() / 3)
    context['target_count'] = target_count
    
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
                new_val = new_val * 2 # 1 - 2 = -1 or -1 + 2 = 1
            elif prev_val + new_val > 1 or prev_val + new_val < -1: #Up or Down vote again
                new_val = -prev_val
                response['msg'] = "You vote has been cancelled."
            else:
                response['msg'] = "You have voted to " + ("up" if new_val > 0 else "down") + "."                
        result_val = prev_val + new_val
        qv.vote_val = result_val            
        qv.save()
        
        response['result_val'] = result_val

        #__gt : greater than / __lt : less than
        vote_count_up = QuestionVote.objects.filter(question=q).filter(vote_val__gt=0).count()
        vote_count_down = QuestionVote.objects.filter(question=q).filter(vote_val__lt=0).count()
        
        response['result_up'] = vote_count_up
        response['result_down'] = vote_count_down
        
        alluserCount = UserProfile.objects.all().exclude(admin=True).count()
        voteCount = QuestionVote.objects.filter(question=qid).filter(vote_val__gt=0).count();


        if voteCount >= target_count:
            q.category = 'cu'
            q.approved = True
            q.save()
            response['suc_msg'] = "This draft questions has been approved."
            #Send email to all who have subscribed.
            title = q.title
            emails = []
            for pf in UserProfile.objects.filter(subscribe_dq=True):
                emails.append(pf.email)
            body = "New question [Title:{} ] has been registered. Now you can answer the questiion. SMF(http://www.uogsmf.org)".format(title)
            send_mail('[SMF] New Question Has Been Approved.',body, 'SMF Notification<2572258p@gmail.com>', emails)

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

        return render(request,'home.html',context)