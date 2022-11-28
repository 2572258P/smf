#from django.shortcuts import render
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import loader
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from .forms import UserForm,UserProfileForm
from django.contrib.auth.models import User


from .models import Question,Choice,Answer,UserProfile,LastAccUser


def vote(request, question_id):
    question = get_object_or_404(Question,pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        
    except (KeyError,Choice.DoesNotExist):
        return render(request,'detail.html',{'question':question,"error_message": "You didn't select a choice.",})
    else:
        print(request.POST['choice'])
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('main:results', args=(question.id,)))

def data_management(request):
    questions = Question.objects.all()
    answers = {}

    last_user = LastAccUser.objects.first();
    print(last_user)

    if 'Load' in request.POST:
        print("Load")        
        try:
            foundUser = User.objects.get(username=request.POST['userId'])
            print("found user:" + request.POST['userId'])
        except:
            print("user does not exist")
        else:
            if foundUser:
                for ans in Answer.objects.all():
                    answers[ans.question_id] = ans.choice_id

    if 'Save' in request.POST:
        print("Save")
        try:
            print(request.POST['userId'])
            foundUser = User.objects.get(username=request.POST['userId'])
        except:
            print("user does not exist")
        else:
            if foundUser:
                for q in Question.objects.all():
                    print(q.pk)
                    choice_id = "choice" + str(q.pk)
                    if choice_id in request.POST:
                        ans = Answer.objects.filter(question_id=q.pk).first()
                        if ans:
                            ans.choice_id = request.POST[choice_id]
                            ans.save()
                        else:
                            userprofile = UserProfile.objects.get(user = foundUser)
                            new_ans = Answer(user = userprofile,question_id=q.pk,choice_id=request.POST[choice_id])
                            new_ans.save()
        print(request.POST)
    if 'Find' in request.POST:        
        lastUser = LastAccUser.objects.get_or_create(lastUser=request.POST['userId'])
        return redirect('main:search_result')

    return render(request,'data_management.html',{'questions':questions,'answers':answers,'last_user':last_user})

def search_reslt(request):
    return HttpResponse("Show Results")

def index(request):
    latest_question_list = Question.objects.order_by('pub_date') #sort in ascending order
    output = '<br>'.join([q.question_text for q in latest_question_list])
    template = loader.get_template('index.html')
    context = {'latest_question_list' : latest_question_list}
    #return HttpResponse(template.render(context,request))
    return render(request,'index.html',context)

def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except:
        raise Http404("Question does not exist")

    #data = [c.choice_text for c in question.choice_set.all()]    
    #return HttpResponse(data)
    
    return render(request,'detail.html',{'question':question})

def results(request, question_id):    
    question = get_object_or_404(Question,pk=question_id)

    return render(request,'results.html',{'question':question})


def registration(request):
    print("registration - started")
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            profile.save();
            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    print("registration - %s" % registered)
    con_dic = {'user_form' : user_form,'profile_form':profile_form,'registered':registered}
    return render(request,'registration.html', context = con_dic)


def test(request):
    return render(request,'registration.html',{})    