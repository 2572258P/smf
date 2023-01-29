from .models import Question,Answer,UserProfile,Choice,InvData,Update#,STF
from collections import defaultdict
from django.contrib.auth.models import User
import time

from sentence_transformers import SentenceTransformer, util
from .view_handler_common import  GetWeightByPriority,CheckAuth,ShowNotAuthedPage,is_ajax
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.utils import timezone
from django.core.mail import send_mail

def s_to_f(obj):
    return round(float(obj),3)


class STF():
    """
    Purpose of the class
    1. caching the calculated results with similarities
    2. providing utilities for NLP
    """
    words = []
    scores = []
    initialized = False
    @staticmethod
    def Init():
        
        if STF.initialized == True:
            return
        STF.initialized = True

        STF.model = SentenceTransformer('all-MiniLM-L6-v2')
        #STF.model = SentenceTransformer('all-mpnet-base-v2')
        #STF.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        
        
        for c in Choice.objects.all():
            if c.choice_text in STF.words:
                continue
            STF.words.append(c.choice_text)
        STF.calculate()
    @staticmethod
    def Update():
        updated = False
        words = [ ch.choice_text for ch in Choice.objects.all() ]

        for word in words:
            if word in STF.words:
                continue
            updated = True
            STF.words.append(word)
        if updated == True:
            STF.calculate()

    @staticmethod
    def getScore(word1,word2):
        if word1 not in STF.words or word2 not in STF.words:
            return 0
        idx1 = STF.words.index(word1)
        idx2 = STF.words.index(word2)
        return s_to_f(STF.scores[idx1][idx2])

    @staticmethod
    def calculate():
        #Compute embedding for both lists        
        if len(STF.words) <= 0: 
            return
        embeddings1 = STF.model.encode(STF.words, convert_to_tensor=True)
        embeddings2 = STF.model.encode(STF.words, convert_to_tensor=True)

        #Compute cosine-similarities
        STF.scores = util.cos_sim(embeddings1, embeddings2)
    @staticmethod
    def calculate_single_similarities(sen1,sen2):
        #Compute embedding for both lists
        embeddings1 = STF.model.encode([sen1], convert_to_tensor=True)
        embeddings2 = STF.model.encode([sen2], convert_to_tensor=True)

        #Compute cosine-similarities
        cosine_scores = util.cos_sim(embeddings1, embeddings2)

        return s_to_f(cosine_scores[0][0])
    @staticmethod
    def calculate_similarities(array1,array2):
        #Compute embedding for both lists
        embeddings1 = STF.model.encode(array1, show_progress_bar=True)
        embeddings2 = STF.model.encode(array2, show_progress_bar=True)

        #Compute cosine-similarities
        cosine_scores = util.cos_sim(embeddings1, embeddings2)

        return cosine_scores
    @staticmethod
    def gen_sim_table_from_tbq(myProfile):
        tbqs = Question.objects.filter(type='tbq').exclude(approved=False)
        table = {}
        for tbq in tbqs:
            table[tbq.id] = {}
            otherAnsArr = []
            myAnsArr = []
            allOtherUsers = UserProfile.objects.all().exclude(user=myProfile.user)            
            myans = Answer.objects.filter(question_id = tbq.id,profile=myProfile).first()
            myAnsArr.append( myans.answer_text if myans != None else "")
            for OUP in allOtherUsers:
                otherAns = Answer.objects.filter(question_id = tbq.id,profile=OUP).first()
                otherAnsArr.append( otherAns.answer_text if otherAns != None else "")
            print("---- Start NLP Operation -----")
            startTime = time.time()
            simResult = STF.calculate_similarities(myAnsArr,otherAnsArr)
            print("----- End NLP Operation Time: {}s".format(time.time()-startTime))
            i = 0
            for OUP in allOtherUsers:
                table[tbq.id][OUP.user.username] = s_to_f(simResult[0][i])
                i += 1
        return table

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
                            score = STF.getScore(mct,oct)
                            highestScore = score if highestScore < score else highestScore 
                        except Exception as e:
                            print(e)
                    weight += highestScore
            elif self.match_type == 'xor':
                if myChoice not in otherAns.choices:
                    weight += 1

        if weight > 0: #When a question type is scq or mcq
            print(" ----- weight per choice {}".format(weight))
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

class SearchEntity:
    def __init__(self,pk,percent):
        self.percent = percent
        self.pf_pk = pk
        self.profile_text = ""
        self.QTs = []
        self.Anss = []

        profile = UserProfile.objects.filter(pk=self.pf_pk).first()
        if profile and profile.profile_text_open == True:
            self.profile_text = profile.profile_text
        else:
            self.profile_text = "This user has disabled the option \"Open Profile Texts In Search\"."
        
        for q in Question.objects.all():
            ans_models = Answer.objects.filter(question_id=q.pk,profile=profile)
            if ans_models.count() == 0:
                continue
            self.QTs.append(q.title)
            ans_ls = []
            for am in ans_models:
                if len(am.answer_text) <= 0: #non-text-based
                    ch = Choice.objects.filter(pk=am.choice_id).first()
                    if ch:
                        ans_ls.append(ch.choice_text)
                else:
                    ans_ls.append(am.answer_text)
            self.Anss.append(ans_ls)
        

    def getPercent(self):
        return self.percent

        


def handle_search_result(request,username):
    myUser = User.objects.get(username=username)
    myProfile = UserProfile.objects.get(user=myUser)
    allUserProfiles = UserProfile.objects.all()
    searchEntities = []
    context = {}

    STF.Init()
    STF.Update()
    AllAnswerWeightTable_tbq = STF.gen_sim_table_from_tbq(myProfile)

    myEntity = SearchEntity(myProfile.pk,100) 
    searchEntities.append(myEntity)

    myQnATable = gen_table_by_answers(Answer.objects.filter(profile=myProfile))
    for OUP in allUserProfiles: #iterate all other users' profiles and calulation weight with mine
        if OUP.user.username == username or OUP.user.username == 'admin': #except myself and admin
            continue
        otherQnATable = gen_table_by_answers(Answer.objects.filter(profile=OUP))
        accWeight = 0
        totalWeight = 0

        for myQId in myQnATable.keys():            
            qo = Question.objects.filter(pk=myQId).first()
            priorityWeight = GetWeightByPriority(qo.priority) if qo != None else 0
            totalWeight = totalWeight + priorityWeight

            if myQId in otherQnATable: #if the other users have the same questions with me
                accWeight += myQnATable[myQId].calcChoiceWeight(otherQnATable[myQId]) * priorityWeight                
            if myQId in AllAnswerWeightTable_tbq:
                accWeight += AllAnswerWeightTable_tbq[myQId][OUP.user.username] * priorityWeight

        if len(otherQnATable) > 0 and totalWeight > 0:
            entity = SearchEntity(OUP.pk,round(accWeight / totalWeight,2) * 100)
            searchEntities.append(entity)

    context['search_results'] = sorted(searchEntities,key = SearchEntity.getPercent,reverse=True)    

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
Message:{}\n\
Please visit our webiste check the \"My Mates\" menu.\n\
http://18.170.55.54/main/my_mates/".format(Inv.message if len(Inv.message) > 0 else "No Message Attached.")



def handle_sending_message(request):
    data = {}
    to_pk = request.POST.get('pf_pk', None)    
    mp = UserProfile.objects.filter(user=request.user).first()
    tp = UserProfile.objects.filter(pk=to_pk).first()
    if tp:        
        msg = request.POST.get('msg',"")
        Inv = InvData(from_pk=mp.pk,to_pk=to_pk,message=msg,time=timezone.localtime(timezone.now()).time() ,date=timezone.localtime(timezone.now()).date())
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

def handle_find_mates(request):
    if CheckAuth(request) is False:
        print("show auth page")
        return ShowNotAuthedPage()

    context = {}
    category_pair = {"cc":"Common Questions","cd":"Details","cb":"Behavioral Questions","cu":"Registered by users"}
    apv_qs = Question.objects.all().exclude(approved=False)
    context['cat_qs'] = {}
    for k,v in category_pair.items():
        context['cat_qs'][k] = apv_qs.filter(category=k)
    context['category_pair'] = category_pair
    context['questions'] = Question.objects.all().exclude(approved=False)
    context['answers'] = {}
    profile = UserProfile.objects.filter(user=request.user).first()
    if profile:
        if 'Find' in request.POST:
            return redirect('main:start_searching',userId=request.user.username)
        elif 'Save' in request.POST:
            context['message'] = "Data have been successfully saved."        
            handle_save(request,profile)        
        else:
            context['message'] = "Data have been successfully loaded."
            
        context['answers'] = handle_load(request,profile)                
        return render(request,'find_mates.html',context)
    else:
        return HttpResponse("{} User Profile Does not Exist".format(request.user))