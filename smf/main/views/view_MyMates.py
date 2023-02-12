from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from .view_Base import is_ajax,CheckAuth,ShowNotAuthedPage
from main.models.models import Question,Answer,UserProfile,InvData,Update
from ..modules.module_NLP import NLP
from ..modules.module_search import SearchEntity,getSeachEntity

class mymate_info:
    def __init__(self):
        self.status = ""
        self.to_pk = -1
        self.email = ''
        self.msg = ''
        self.time = ''
        self.date = ''
        self.profile_text = ''
        self.username = ''
        self.se = None

def GetBodyTextForSuccess(Inv):
    return "Congratulations! your request has been accepted by the other user. \n\n\
Message: {}\n\
Please visit our webiste and check the \"My Mates\" menu.\n\
http://18.170.55.54/main/my_mates/".format( Inv.message if len(Inv.message) > 0 else "No Message Attached.")

def loadpage(request):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()

    NLP.Init()
    
    if is_ajax(request):
        cmd = request.POST.get('cmd')
        data = {}
        mp_pk = UserProfile.objects.filter(user=request.user).first().pk

        if cmd == 'cancel':
            to_pk = request.POST.get('to_pk')
            inv = InvData.objects.filter(from_pk=mp_pk,to_pk=to_pk,accepted=False).first()
            if inv:
                inv.delete()
        elif cmd == 'accept':            
            to_pk = request.POST.get('to_pk')
            inv = InvData.objects.filter(from_pk=to_pk,to_pk=mp_pk,accepted=False).first()
            mp = UserProfile.objects.filter(user=request.user).first()
            tp = UserProfile.objects.filter(pk=to_pk).first()
            if inv:
                inv.accepted = True
                body = GetBodyTextForSuccess(inv)
                send_mail('[SMF] Your request has been accepted.',body, 'SMF Notification<2572258p@gmail.com>', [tp.email])

                inv.date = timezone.localtime(timezone.now()).date()
                inv.time = time=timezone.localtime(timezone.now()).time()
                inv.save()

                up = Update(profile=mp,to_pk=to_pk)
                up.save()
                up = Update(profile=tp,to_pk=mp_pk)
                up.save()
        elif cmd == 'reject':
            to_pk = request.POST.get('to_pk')
            inv = InvData.objects.filter(from_pk=to_pk,to_pk=mp_pk,accepted=False).first()
            if inv:
                inv.delete()
        elif cmd == 'disconnect':
            to_pk = request.POST.get('to_pk')
            inv = InvData.objects.filter(from_pk=mp_pk,to_pk=to_pk,accepted=True) | InvData.objects.filter(from_pk=to_pk,to_pk=mp_pk,accepted=True)
            inv.delete()
        return JsonResponse(data)
    else:
        context = {}

        mp = UserProfile.objects.filter(user=request.user).first()
        my_pk = mp.pk
        sent_data = InvData.objects.filter(from_pk=my_pk,accepted=False)
        rev_data = InvData.objects.filter(to_pk=my_pk,accepted=False)
        acc_data = InvData.objects.filter(from_pk=my_pk,accepted=True) | InvData.objects.filter(to_pk=my_pk,accepted=True)

        # Get a precomputed similarity table with my mates
        otherUserPfs = []
        for invd in sent_data | rev_data | acc_data:
            target_pk = invd.from_pk if my_pk != invd.from_pk else invd.to_pk
            otherUserPfs.append(UserProfile.objects.filter(pk=target_pk).first())

        SimDictTable_tbq = NLP.gen_sim_dict_from_tbq(mp,otherUserPfs)

        context['mates'] = {}
        labels = {'req':'Requested', 'rev':'Received', 'acc':'Connected'}
        context['labels'] = labels
        for key in labels:
            context['mates'][key] = []
        
        # Create MyMateInfo for all
        for invd in sent_data | rev_data | acc_data:
            status = ''
            target_pk = -1
            mi = mymate_info()
            target_pk = invd.from_pk if my_pk != invd.from_pk else invd.to_pk
            if invd.accepted: #accepted
                mi.status = 'acc'
            elif invd.from_pk == my_pk:  #requested
                mi.status = 'req'
            elif invd.to_pk == my_pk: #received
                mi.status = 'rev'            

            op = UserProfile.objects.filter(pk = target_pk).first()
            if op == None:
                continue

            mi.to_pk = target_pk
            mi.email = op.email        
            mi.msg = invd.message
            mi.profile_text = op.profile_text
            mi.time = invd.time
            mi.date = invd.date
            mi.username = op.user.username
            se = getSeachEntity(mp,op,SimDictTable_tbq)
            mi.se = se
            context['mates'][mi.status].append(mi)

        #Update Checks
        context['updates'] = {}
        for ud in Update.objects.filter(profile=mp).all():
            context['updates'][ud.to_pk] = ud.to_pk
        Update.objects.filter(profile=mp).delete()

        return render(request, 'my_mates.html',context)