from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.mail import send_mail

from datetime import datetime
from datetime import date

from main.models.models import Question,Answer,UserProfile,InvData,Update

from .view_Base import is_ajax
from ..modules.module_NLP import NLP
from ..modules.module_search import SearchEntity,getSeachEntity



def GetBodyTextForRequest(Inv):
    return "A user in SMF service requested you.\n\n\
Message: {}\n\
Please visit our webiste check the \"My Mates\" menu.\n\
http://18.170.55.54/main/my_mates/".format(Inv.message if len(Inv.message) > 0 else "No Message Attached.")



def handle_sending_message(request):
    data = {}
    to_pk = request.POST.get('pf_pk', None)    
    mp = UserProfile.objects.filter(user=request.user).first()
    tp = UserProfile.objects.filter(pk=to_pk).first()
    if tp:
        msg = request.POST.get('msg',"")        
        now = datetime.now()
        today = date.today()
        time = now.strftime("%H:%M:%S")


        Inv = InvData(from_pk=mp.pk,to_pk=to_pk,message=msg,time=time ,date=today)
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
    myProfile = UserProfile.objects.get(user=User.objects.get(username=username))
    searchEntities = []
    context = {}

    allOtherUsers = UserProfile.objects.all().exclude(user=myProfile.user)
    SimDictTable_tbq = NLP.gen_sim_dict_from_tbq(myProfile,allOtherUsers)
    myse = SearchEntity() 
    myse.generateAll(myProfile,100,myProfile,100,100)
    searchEntities.append(myse)

    
    for oup in allOtherUsers: #iterate all other users' profiles and calulation weight with mine
        if oup.user.username == username or oup.user.username == 'admin': #except myself and admin
            continue

        otherEntity = getSeachEntity(myProfile,oup,SimDictTable_tbq)
        if otherEntity:
            searchEntities.append(otherEntity)
                
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

 