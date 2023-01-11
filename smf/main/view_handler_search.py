from .models import Question,Answer,UserProfile,Choice#,STF
from collections import defaultdict
from django.contrib.auth.models import User
import time

from sentence_transformers import SentenceTransformer, util

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
        return STF.scores[idx1][idx2]

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

        return cosine_scores[0][0]
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
            print(myAnsArr)
            print(otherAnsArr)
            startTime = time.time()
            simResult = STF.calculate_similarities(myAnsArr,otherAnsArr)
            print("----- End NLP Operation Time: {}s".format(time.time()-startTime))
            i = 0
            for OUP in allOtherUsers:
                table[tbq.id][OUP.user.username] = simResult[0][i]
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
        if weight > 0: #When a question type is scq or mcq
            return weight / len(self.choices)
        return 0


class Resultinfo():
    def __init__(self,userid,percent):
        self.percent = percent
        self.userid = userid
    def getPercent(self):
        return self.percent

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

def GetWeightByPriority(priority):
    if priority == 'high':
        return 1
    if priority == 'medium':
        return 0.66
    if priority == 'low':
        return 0.33
    return 1

def handle_search_result(username):
    myUser = User.objects.get(username=username)
    myProfile = UserProfile.objects.get(user=myUser)
    allUserProfiles = UserProfile.objects.all()
    resultInfos = []

    STF.Init()
    STF.Update()
    AllAnswerWeightTable_tbq = STF.gen_sim_table_from_tbq(myProfile)

    myQnATable = gen_table_by_answers(Answer.objects.filter(profile=myProfile))
    for OUP in allUserProfiles: #iterate all other users' profiles and calulation weight with mine
        if OUP.user.username == username or OUP.user.username == 'admin': #except myself and admin
            continue
        otherQnATable = gen_table_by_answers(Answer.objects.filter(profile=OUP))
        totalWeight = 0

        for myQId in myQnATable.keys():
            
            qo = Question.objects.filter(pk=myQId).first()
            priorityWeight = GetWeightByPriority(qo.priority) if qo != None else 0            

            if myQId in otherQnATable: #if the other users have the same questions with me
                totalWeight += myQnATable[myQId].calcChoiceWeight(otherQnATable[myQId]) * priorityWeight
            if myQId in AllAnswerWeightTable_tbq:
                totalWeight += AllAnswerWeightTable_tbq[myQId][OUP.user.username] * priorityWeight
                
        if len(otherQnATable) > 0:
            resultInfos.append(Resultinfo(OUP.user.username,totalWeight / len(myQnATable) * 100))
    sr = sorted(resultInfos,key = Resultinfo.getPercent,reverse=True)
    return sr