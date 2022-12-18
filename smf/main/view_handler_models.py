
from .models import Question,Answer,UserProfile,STF
from collections import defaultdict
from django.utils import timezone

def handle_load(request,profile):
    answers = {}

    if profile:
        for ans in Answer.objects.filter(profile=profile):            
            if ans.question_id not in answers:
                answers[ans.question_id] = []
            if ans.choice_id != -1:
                answers[ans.question_id].append(ans.choice_id)
            answers[ans.question_id].append(ans.answer_text)
            print(answers[ans.question_id])
    return answers
    
def handle_save(request,profile):
    for q in Question.objects.all():
        anss = Answer.objects.filter(profile=profile,question_id=q.pk)
        anss.delete()
        if q.type == 'scq' or q.type == 'mcq':
            c_id = "choice" + str(q.pk)
            if q.type == 'scq':
                a = Answer(profile=profile,question_id=q.pk,choice_id=request.POST.get(c_id,-1))
                a.save()
            elif q.type == 'mcq':
                for ans in request.POST.getlist(c_id):
                    a = Answer(profile=profile,question_id=q.pk,choice_id=ans)
                    a.save()
        elif q.type == 'tbq':
            a = Answer(profile=profile,question_id=q.pk,answer_text=request.POST["text_ans%i"%q.id])
            a.save()

def handle_createQuestion(request,question_type):
    scq_text = request.POST.get('scq_text','')
    mcq_text = request.POST.get('mcq_text','')
    tbq_text = request.POST.get('tbq_text','')
    scq_choice_num = range(1,11)
    mcq_choice_num = range(1,11)
    message = ''
    if scq_text == '' and mcq_text == '' and tbq_text == '':
        message = 'Enter questions and choices with types at least one'
    else:
        choiceWords = []
        if scq_text != '':
            q = Question(type="scq",ctrl_type='radio',question_text=scq_text,pub_date=timezone.now())        
            q.save()
            for i in scq_choice_num:
                choice_text = request.POST.get("scq_c%i"%i,'')                
                if choice_text != '':
                    q.choice_set.create(choice_text=choice_text)
                    choiceWords.append(choice_text)
        if mcq_text != '':
            q = Question(type="mcq",ctrl_type='checkbox',question_text=mcq_text,pub_date=timezone.now())        
            q.save()
            for i in mcq_choice_num:
                choice_text = request.POST.get("mcq_c%i"%i,'')
                if choice_text != '':
                    q.choice_set.create(choice_text=choice_text)
                    choiceWords.append(choice_text)
        if tbq_text != '':
            q = Question(type="tbq",ctrl_type='textarea',question_text=tbq_text,pub_date=timezone.now())        
            q.save()
        STF.Update(choiceWords)
    return {'message':message,'scq_choice_num':scq_choice_num,'mcq_choice_num':mcq_choice_num,'selectedType':question_type}