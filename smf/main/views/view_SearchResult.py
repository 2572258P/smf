from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail

from main.models.models import Question,Answer,UserProfile,InvData,Update

from .view_Base import is_ajax
from ..modules.module_common import GetWeightByPriority
from ..modules.module_NLP import NLP
from ..modules.module_search import gen_table_by_answers,SearchEntity,WeightCalculator



def GetBodyTextForRequest(Inv):
    return "A user in SMF service requested you.\n\n\
Message: {}\n\
Match Percent: {}%\n\
Please visit our webiste check the \"My Mates\" menu.\n\
http://18.170.55.54/main/my_mates/".format(Inv.message if len(Inv.message) > 0 else "No Message Attached.",Inv.percent)


def handle_sending_message(request):
    data = {}
    to_pk = request.POST.get('pf_pk', None)    
    mp = UserProfile.objects.filter(user=request.user).first()
    tp = UserProfile.objects.filter(pk=to_pk).first()
    if tp:
        msg = request.POST.get('msg',"")
        percent = float(request.POST.get('percent',0))
        Inv = InvData(percent=percent,from_pk=mp.pk,to_pk=to_pk,message=msg,time=timezone.localtime(timezone.now()).time() ,date=timezone.localtime(timezone.now()).date())
        Inv.save()
        body = GetBodyTextForRequest(Inv)
        send_mail('[SMF] Request Message',body, 'SMF Notification<2572258p@gmail.com>', [tp.email])
        up = Update(profile=tp,to_pk=mp.pk)
        up.save()
    else:
        print('no user found.')
    
    return JsonResponse(data)

def handle_search_result(request,username):
    NLP.Init()
    NLP.Update()
    myUser = User.objects.get(username=username)
    myProfile = UserProfile.objects.get(user=myUser)
    allUserProfiles = UserProfile.objects.all()
    searchEntities = []
    context = {}

    AllAnswerWeightTable_tbq = NLP.gen_sim_table_from_tbq(myProfile)
    myse = SearchEntity() 
    myse.generateAll(myProfile.pk,100,myProfile,100,100)
    searchEntities.append(myse)

    myQnATable = gen_table_by_answers(Answer.objects.filter(profile=myProfile))
    
    for oup in allUserProfiles: #iterate all other users' profiles and calulation weight with mine
        if oup.user.username == username or oup.user.username == 'admin': #except myself and admin
            continue
        otherQnATable = gen_table_by_answers(Answer.objects.filter(profile=oup))        
        accPoint = 0
        totalPoint = 0
        ose = SearchEntity()

        for myQId in myQnATable.keys():
            qo = Question.objects.filter(pk=myQId).first()

            priorityWeight = GetWeightByPriority(qo.priority) if qo != None else 0
            totalPoint = totalPoint + priorityWeight
            ose.addCatTotalScore(qo.category,priorityWeight)

            score = 0
            if myQId in otherQnATable: #if the other users have the same questions with me
                score = myQnATable[myQId].calcChoiceWeight(otherQnATable[myQId]) * priorityWeight                
            if myQId in AllAnswerWeightTable_tbq:
                score = AllAnswerWeightTable_tbq[myQId][oup.user.username] * priorityWeight
            accPoint += score
            ose.addCatScore(qo.category,score)

            
        if len(otherQnATable) > 0 and totalPoint > 0:
            accPoint = round(accPoint,2)
            percent = round(accPoint / totalPoint * 100,2)
            totalPoint = round(totalPoint,2)
            ose.generateAll(oup.pk,percent,myProfile,accPoint,totalPoint)
            searchEntities.append(ose)
    
    context['search_entities'] = sorted(searchEntities,key = SearchEntity.getAccPoint,reverse=True)    

    
    #Status with others
    context['sent'] = {}
    for s in InvData.objects.filter(from_pk=myProfile.pk,accepted=False):
        context['sent'][s.to_pk] = s.to_pk
    context['rev'] = {}
    for s in InvData.objects.filter(to_pk=myProfile.pk,accepted=False):
        context['rev'][s.from_pk] = s.from_pk
    context['con'] = {}
    for s in InvData.objects.filter(from_pk=myProfile.pk,accepted=True) | InvData.objects.filter(to_pk=myProfile.pk,accepted=True):
        pk = s.from_pk if s.from_pk != myProfile.pk else s.to_pk
        context['con'][pk] = pk


    return render(request, 'search_results.html',context)



def loadpage(request,username):
    if is_ajax(request):        
        return handle_sending_message(request)
    else:
        return handle_search_result(request,username)

 