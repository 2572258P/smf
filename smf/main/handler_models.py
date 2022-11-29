
from .models import Question,Answer,UserProfile


def handle_load(request,profile):
    answers = {}
    if profile:
        for ans in Answer.objects.filter(profile=profile):
            answers[ans.question_id] = ans.choice_id
    return answers


def handle_save(request,profile):
    for q in Question.objects.all():
        choice_id = "choice" + str(q.pk)
        if choice_id in request.POST:
            print("choice id %s" % choice_id)
            ans = Answer.objects.filter(question_id=q.pk,profile=profile).first()
            if ans:
                print("exist!")
                print(ans)
                print(request.POST[choice_id])
                ans.choice_id = request.POST[choice_id]
                ans.save()
            else:
                print("new!")
                userprofile = UserProfile.objects.get(user=profile.user)
                print(request.POST[choice_id])
                new_ans = Answer(profile = userprofile,question_id=q.pk,choice_id=request.POST[choice_id])
                new_ans.save()


    