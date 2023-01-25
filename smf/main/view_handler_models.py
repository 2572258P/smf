
from .models import Question,Answer,UserProfile#,STF
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

def handle_createQuestion(request,question_type,profile):
    scq_text = request.POST.get('scq_text','')
    mcq_text = request.POST.get('mcq_text','')
    tbq_text = request.POST.get('tbq_text','')
    category = request.POST.get('category','')
    priority = request.POST.get('mPri','')
    match_type = request.POST.get('mType','smt') #default value 'smt'

    scq_choice_num = range(1,21)
    mcq_choice_num = range(1,21)
    message = ''
    if scq_text == '' and mcq_text == '' and tbq_text == '':
        if question_type == 'tbq':
            message = 'Text-Based Question - Enter your question'
        elif question_type == 'scq':            
            message = 'Single-Choice Question - Enter a question and choices.'
        elif question_type == 'mcq':
            message = 'Multiple-Choice Question - Enter a question and choices.'        
    else:
        try:            
            if len(scq_text) > 0:
                q = Question(approved=profile.admin,type="scq",ctrl_type='radio',title=scq_text,pub_date=timezone.now(),priority = priority,match_type = match_type,category=category)
                q.save()
                for i in scq_choice_num:
                    choice_text = request.POST.get("scq_c%i"%i,'')                
                    if choice_text != '':
                        q.choice_set.create(choice_text=choice_text)
            if len(mcq_text) > 0:
                q = Question(approved=profile.admin,type="mcq",ctrl_type='checkbox',title=mcq_text,pub_date=timezone.now(),priority = priority,match_type = match_type,category=category)
                q.save()
                for i in mcq_choice_num:
                    choice_text = request.POST.get("mcq_c%i"%i,'')
                    if choice_text != '':
                        q.choice_set.create(choice_text=choice_text)
            if len(tbq_text) > 0:
                desc = request.POST.get('tbq_desc')
                q = Question(approved=profile.admin,type="tbq",ctrl_type='textarea',title=tbq_text,desc=desc,pub_date=timezone.now(),priority = priority,match_type = match_type,category=category)
                q.save()
            message = 'New question has been successfully created.'

        except Exception as inst:
            print(inst)
        
    return {'message':message,'scq_choice_num':scq_choice_num,'mcq_choice_num':mcq_choice_num,'selectedType':question_type}