from .models import Question,Answer,UserProfile,Choice,InvData,Update#,STF
from collections import defaultdict
from django.contrib.auth.models import User
import time

from sentence_transformers import SentenceTransformer, util
from .view_handler_common import  GetWeightByPriority,CheckAuth,ShowNotAuthedPage,is_ajax,GetCategoryLabel
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.utils import timezone
from django.core.mail import send_mail


from .processor_NLP import NLP




class WeightCalculator():
    def __init__(self,match_type):
        self.choices = []
        self.match_type = match_type
    def addChoice(self,choice):
        if choice != -1:
            self.choices.append(choice)    
    def calcChoiceWeight(self,otherAns):
        weight = 0
        for myChoice in self.choices: #when the answers are for Single Choice Questions or Multiple Choice Questons.
            if self.match_type == 'emt':
                if myChoice in otherAns.choices: #if other user has exactly the same answer
                    weight += 1
            elif self.match_type == 'smt': #if other user does not have the same answer, find the highest weighted answer            
                highestScore = 0
                if myChoice in otherAns.choices:
                    weight += 1
                else:
                    for otherUserChoice in otherAns.choices:
                        try:
                            mct = Choice.objects.get(pk=myChoice).choice_text
                            oct = Choice.objects.get(pk=otherUserChoice).choice_text
                            score = NLP.getScore(mct,oct)
                            highestScore = score if highestScore < score else highestScore 
                        except Exception as e:
                            print(e)
                    weight += highestScore
            elif self.match_type == 'xor':
                if myChoice not in otherAns.choices:
                    weight += 1

        if weight > 0: #When a question type is scq or mcq            
            return weight / len(self.choices)
        return 0



def getPercentWithAnswers(mp,op,anss1,anss2):
    totalCount = len(anss1)    
    matchedCount = 0
    for ans1 in anss1:
        matchedAnss = anss2.filter(question_id=ans1.question_id,choice_id=ans1.choice_id)
        for ma in matchedAnss:            
            matchedCount += len(matchedAnss)
    
    return int((matchedCount / totalCount) * 100)

def gen_table_by_answers(ansQueryForAll):
    result = {}
    for ans in ansQueryForAll:
        qo = Question.objects.filter(pk=ans.question_id).first()
        if ans.question_id not in result and qo != None:
            result[ans.question_id] = WeightCalculator(qo.match_type)        
        if ans.question_id in result:
            result[ans.question_id].addChoice(ans.choice_id)

    return result

class CategoryInfo:
    def __init__(self,label):
        self.totalScore = 0
        self.score = 0
        self.per = 0
        self.label = label
    def CalcPercentage(self):
        self.per = int(self.score / self.totalScore * 100)
        print("totalScore:",self.totalScore)
        print("score:",self.score)


def handle_search_result(request,username):
    myUser = User.objects.get(username=username)
    myProfile = UserProfile.objects.get(user=myUser)
    allUserProfiles = UserProfile.objects.all()
    searchEntities = []
    context = {}

    NLP.Init()
    NLP.Update()
    AllAnswerWeightTable_tbq = NLP.gen_sim_table_from_tbq(myProfile)

    me = SearchEntity() 
    me.generateAll(myProfile.pk,100,myProfile)    
    searchEntities.append(me)

    myQnATable = gen_table_by_answers(Answer.objects.filter(profile=myProfile))
    for OUP in allUserProfiles: #iterate all other users' profiles and calulation weight with mine
        if OUP.user.username == username or OUP.user.username == 'admin': #except myself and admin
            continue
        otherQnATable = gen_table_by_answers(Answer.objects.filter(profile=OUP))
        accWeight = 0
        totalWeight = 0
        ose = SearchEntity()

        for myQId in myQnATable.keys():
            qo = Question.objects.filter(pk=myQId).first()

            priorityWeight = GetWeightByPriority(qo.priority) if qo != None else 0
            totalWeight = totalWeight + priorityWeight
            ose.addCatTotalScore(qo.category,priorityWeight)

            score = 0
            if myQId in otherQnATable: #if the other users have the same questions with me
                score = myQnATable[myQId].calcChoiceWeight(otherQnATable[myQId]) * priorityWeight                
            if myQId in AllAnswerWeightTable_tbq:
                score = AllAnswerWeightTable_tbq[myQId][OUP.user.username] * priorityWeight
            accWeight += score
            ose.addCatScore(qo.category,score)

        if len(otherQnATable) > 0 and totalWeight > 0:
            ose.generateAll(OUP.pk,round(accWeight / totalWeight,2) * 100,myProfile)
            searchEntities.append(ose)
    
    context['search_entities'] = sorted(searchEntities,key = SearchEntity.getPercent,reverse=True)    

    
    #Status with others
    context['sent'] = {}
    for s in InvData.objects.filter(from_pk=myProfile.pk,accepted=False):
        context['sent'][s.to_pk] = s.to_pk
    context['rev'] = {}
    for s in InvData.objects.filter(to_pk=myProfile.pk,accepted=False):
        context['rev'][s.from_pk] = s.from_pk

    context['con'] = {}
    for s in InvData.objects.filter(from_pk=myProfile.pk,accepted=True) | InvData.objects.filter(to_pk=myProfile.pk,accepted=True):
        pk = s.from_pk if s.from_pk != myProfile.pk else s.to_pk
        context['con'][pk] = pk


    return render(request, 'search_results.html',context)

def GetBodyText(Inv):
    return "A user in SMF service requested you.\n\n\
Message: {}\n\
Match Percent: {}%\n\
Please visit our webiste check the \"My Mates\" menu.\n\
http://18.170.55.54/main/my_mates/".format(Inv.message if len(Inv.message) > 0 else "No Message Attached.",Inv.percent)



def handle_sending_message(request):
    data = {}
    to_pk = request.POST.get('pf_pk', None)    
    mp = UserProfile.objects.filter(user=request.user).first()
    tp = UserProfile.objects.filter(pk=to_pk).first()
    if tp:        
        msg = request.POST.get('msg',"")
        percent = float(request.POST.get('percent',0))
        Inv = InvData(percent=percent,from_pk=mp.pk,to_pk=to_pk,message=msg,time=timezone.localtime(timezone.now()).time() ,date=timezone.localtime(timezone.now()).date())
        Inv.save()
        body = GetBodyText(Inv)
        send_mail('[SMF] Request Message',body, 'SMF Notification<2572258p@gmail.com>', [tp.email])
        up = Update(profile=tp,to_pk=mp.pk)
        up.save()
    else:
        print('no user found.')
    
    return JsonResponse(data)

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
    for q in Question.objects.all().filter(approved=True):
        anss = Answer.objects.filter(profile=profile,question_id=q.pk)
        anss.delete()
        if q.type == 'scq' or q.type == 'mcq':
            c_id = "choice" + str(q.pk)
            if q.type == 'scq' and request.POST.get(c_id):
                a = Answer(profile=profile,question_id=q.pk,choice_id=request.POST.get(c_id,-1))
                a.save()
            elif q.type == 'mcq':
                for ans in request.POST.getlist(c_id):                    
                    a = Answer(profile=profile,question_id=q.pk,choice_id=ans)
                    a.save()
        elif q.type == 'tbq':
            text_ans = request.POST["text_ans%i"%q.pk]
            if len(text_ans) > 0:
                a = Answer(profile=profile,question_id=q.pk,answer_text=text_ans)
                a.save()


def get_per_ans(mp):
    apv_qs = Question.objects.all().exclude(approved=False) # Get all questions except unapproved Qs
    #Count I have answered
    total_qs_count = apv_qs.count()
    my_anss = Answer.objects.filter(profile=mp)
    ass_count = 0
    duplicated = {}
    for ans in my_anss:
        if Question.objects.filter(pk=ans.question_id).first() and ans.question_id not in duplicated:
            duplicated[ans.question_id] = ans.question_id
            ass_count += 1
    return int(ass_count / total_qs_count * 100)

def handle_find_mates(request):
    if CheckAuth(request) is False:
        return ShowNotAuthedPage()

    apv_qs = Question.objects.all().exclude(approved=False) # Get all questions except unapproved Qs
    mp = UserProfile.objects.filter(user=request.user).first()
    if not mp:
        return HttpResponse("{} User Profile Does not Exist".format(request.user))
    #Total count of approved quetions

    if is_ajax(request): #Saving        
        mp = UserProfile.objects.filter(user=request.user).first()
        handle_save(request,mp)
        data = {"per_ans":get_per_ans(mp)}
        return JsonResponse(data)
    else: #Only for loading
        context = {}
        #labelling for categories    
        category_pair = {"cc":"Common Questions","cd":"Details","cb":"Psychology","cu":"Registered by users"}        
        context['cat_qs'] = {}
        for k,v in category_pair.items():
            context['cat_qs'][k] = apv_qs.filter(category=k)
        context['category_pair'] = category_pair
        context['questions'] = apv_qs
        context['answers'] = {}        
        context['message'] = "Data have been successfully loaded."                
        context['answers'] = handle_load(request,mp)
        context['per_ans'] = get_per_ans(mp)
        return render(request,'find_mates.html',context)
