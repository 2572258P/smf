
from .models import Question,Answer,UserProfile
from collections import defaultdict

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
            