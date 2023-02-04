from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.http import HttpResponse,JsonResponse

from .models import LastAccUser,UserProfile
from .views_commons import is_ajax


def sign_in_page(request):
    return render(request,'sign_in.html',{})

def user_logout(request):
    logout(request)
    return redirect(reverse('main:home'))

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)

                LastAccUser.objects.all().delete()
                lastUser = LastAccUser(lastUser=username)                
                lastUser.save()

                return redirect(reverse('main:home'))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            HttpResponse(f"Invalid login details: {username},{password}")
            return HttpResponse("Invalid login details supplied.")

    return HttpResponse("The request was not POST type")


def registration(request):    
    response = {}
    if is_ajax(request) and request.POST.get('cmd') == 'create':        
        check_username = request.POST.get('check_username')        
        new_username = request.POST.get('username')
        password = request.POST.get('password')        
        success = False

        if new_username is not None and len(new_username) < 5:
            response['msg'] = "User name must be at least five letters."
        elif new_username is not None and re.match("^[A-Za-z0-9_-]*$",new_username) == None:
            response['msg'] = "Special letters are not allowed to use for user name."
        elif User.objects.filter(username = new_username).first():
            response['msg'] = "User name \"{}\" is not available.".format(new_username)
        elif password is not None and len(password) < 8:
            response['msg'] = "Password must to be set eight letters at least."
        else:
            success = True
        response['success'] = success

        if success:
            newuser = User.objects.create_user(username=new_username, password=password)
            userpf = UserProfile(user=newuser,
            profile_text=request.POST.get('pf_text'),
            profile_text_open=request.POST.get('pf_text_open') == 'true',
            email=request.POST.get('email'))
            userpf.save()
            
            user = authenticate(username=new_username,password=password)
            if user and user.is_active:
                login(request,user)

        return JsonResponse(response)
    elif is_ajax(request) and request.POST.get('cmd') == 'test_user_fill':

        profile_auto_texts = ['I want to study with you','I love talking wit others','I want to be a friend of yours.']

        user_count = User.objects.all().count()
        response['test_user_name'] = 'user' + str(user_count)
        response['pw'] = '123456ab!'
        response['pw_confirm'] = '123456ab!'
        response['email'] = '2572258p@gmail.com'
        response['pf_text'] = profile_auto_texts[random.randint(0,len(profile_auto_texts)-1)]
        return JsonResponse(response)
    else:        
        return render(request,'profile_registration.html',{} )

def my_account(request):    
    if is_ajax(request): #Received
        response = {} 
        pf = UserProfile.objects.filter(user=request.user).first()
        if pf:            
            pf.email = request.POST.get('email')
            pf.profile_text = request.POST.get('pf_text')
            pf.profile_text_open = request.POST.get('pf_text_open') == 'true'
            pf.save()
        response['msg'] = "updated"

        return JsonResponse(response)
    else:
        context = {}
        context['username'] = request.user.username
        pf = UserProfile.objects.filter(user=request.user).first()
        if pf:
            context['email'] = pf.email
            context['pf_text'] = pf.profile_text
            context['pf_text_open'] = 'True' if pf.profile_text_open == True else 'False'
            
        return render(request,'profile_management.html',context )
