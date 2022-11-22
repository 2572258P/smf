#from django.shortcuts import render
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.template import loader
from django.shortcuts import render,get_object_or_404
from django.urls import reverse

from .models import Question
from .models import Choice

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[0:5] #sort in ascending order
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

def vote(request, question_id):
    question = get_object_or_404(Question,pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        
    except (KeyError,Choice.DoesNotExist):
        return render(request,'detail.html',{'question':question,"error_message": "You didn't select a choice.",})
    else:
        selected_choice.votes += 1
        selected_choice.save()

        return HttpResponseRedirect(reverse('main:results', args=(question.id,)))

