
from .models import Question,Answer,UserProfile
from collections import defaultdict

def handle_load(request,profile):
    answers = {}

    if profile:
        for ans in Answer.objects.filter(profile=profile):
            if ans.question_id not in answers:
                answers[ans.question_id] = []            
            answers[ans.question_id].append(ans.choice_id)

    return answers
    
def handle_save(request,profile):    
    for q in Question.objects.all():
        anss = Answer.objects.filter(profile=profile,question_id=q.pk)
        anss.delete()
        choice_id = "choice" + str(q.pk)
        if q.type == 'scq':            
            a = Answer(profile=profile,question_id=q.pk,choice_id=request.POST[choice_id])
            a.save()
        elif q.type == 'mcq':
            for ans in request.POST.getlist(choice_id):
                a = Answer(profile=profile,question_id=q.pk,choice_id=ans)
                a.save()