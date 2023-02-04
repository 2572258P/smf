from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from .view_Base import is_ajax,CheckAuth,ShowNotAuthedPage
from main.models.models import Question,Answer,UserProfile,InvData,Update

class mymate_info:
    def __init__(self,to_pk,date="",time="",msg="",email="",profile_text="",username="",percent=0):
        self.percent = percent
        self.to_pk = to_pk
        self.email = email
        self.msg = msg
        self.time = time
        self.date = date
        self.profile_text = profile_text
        self.username = username

def GetBodyTextForSuccess(Inv):
    return "Congratulations! your request has been accepted by the other user. \n\n\
Message: {}\n\
Match Percent: {}%\n\
Please visit our webiste and check the \"My Mates\" menu.\n\
http://18.170.55.54/main/my_mates/".format( Inv.message if len(Inv.message) > 0 else "No Message Attached.",Inv.percent)

def loadpage(request):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()

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
        sent_data = InvData.objects.filter(from_pk=mp.pk,accepted=False)
        rev_data = InvData.objects.filter(to_pk=mp.pk,accepted=False)
        acc_data = InvData.objects.filter(from_pk=mp.pk,accepted=True) | InvData.objects.filter(to_pk=mp.pk,accepted=True)
        context['sent'] = []
        context['rev']  = []
        context['acc']  = []

        for sd in sent_data:
            context['sent'].append(mymate_info(date=str(sd.date),time=sd.time.strftime('%I:%H %p'),to_pk=sd.to_pk,msg=sd.message,percent=sd.percent))
        for rv in rev_data:
            context['rev'].append(mymate_info(date=str(rv.date),time=rv.time.strftime('%I:%H %p'),to_pk=rv.from_pk,msg=rv.message,percent=rv.percent))
        for ac in acc_data:
            connected_pk = ac.to_pk if ac.from_pk == mp.pk else ac.from_pk
            up = UserProfile.objects.filter(pk=connected_pk).first()
            context['acc'].append(mymate_info(date=str(ac.date),time=ac.time.strftime('%I:%H %p'),to_pk=connected_pk,msg=ac.message,email=up.email,profile_text=up.profile_text,percent=ac.percent))
        

        context['updates'] = {}
        for ud in Update.objects.filter(profile=mp).all():
            context['updates'][ud.to_pk] = ud.to_pk
        Update.objects.filter(profile=mp).delete()

        return render(request, 'my_mates.html',context)