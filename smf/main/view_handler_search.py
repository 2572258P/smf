from .models import Question,Answer,UserProfile,Choice#,STF
from collections import defaultdict
from django.contrib.auth.models import User
import time

from sentence_transformers import SentenceTransformer, util

class STF():
    """
    what it does
    1. caching the calculated results with similarities
    2. providing utilities
    """
    words = []
    scores = []
    initialized = False
    @staticmethod
    def init():
        
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
        STF.init()
        STF.Update()

        #Compute embedding for both lists
        embeddings1 = STF.model.encode(array1, show_progress_bar=True)
        embeddings2 = STF.model.encode(array2, show_progress_bar=True)

        #Compute cosine-similarities
        cosine_scores = util.cos_sim(embeddings1, embeddings2)

        return cosine_scores
    @staticmethod
    def gen_sim_table_from_tbq(myProfile):
        tbqs = Question.objects.filter(type='tbq')
        table = {}
        for tbq in tbqs:
            table[tbq.id] = {}
            answers = Answer.objects.filter(question_id = tbq.id)
            otherUserNames = []
            myTextAns = []
            otherTextAns = []

            for ans in answers:
                if ans.profile == myProfile:
                    myTextAns.append(ans.answer_text)
                else:
                    otherTextAns.append(ans.answer_text)
                    otherUserNames.append(ans.profile.user.username)

            print("---- Start NLP Operation -----")
            startTime = time.time()
            simResult = STF.calculate_similarities(myTextAns,otherTextAns)
            i = 0
            for oun in otherUserNames:
                table[tbq.id][oun] = simResult[0][i]
                i += 1
            
            print("End NLP Operation Time: {}s".format(time.time()-startTime))
        return table




class SCQ_MCQ_Ansdata():
    def __init__(self):
        self.choices = []
    def addChoice(self,choice):
        if choice != -1:
            self.choices.append(choice)    
    def calcChoiceWeight(self,otherAns):
        weight = 0
        for mc in self.choices: #when the answers are for Single Choice Questions or Multiple Choice Questons.
            if mc in otherAns.choices:
                weight += 1
            else:
                highestScore = 0
                for oc in otherAns.choices:
                    try:
                        mct = Choice.objects.get(pk=mc).choice_text
                        oct = Choice.objects.get(pk=oc).choice_text
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

def gen_table_scq_mcq(ansQuery):
    result = {}
    for ans in ansQuery:
        if ans.question_id not in result:
            result[ans.question_id] = SCQ_MCQ_Ansdata()
        result[ans.question_id].addChoice(ans.choice_id)
    return result



def handle_search_result(username):
    myUser = User.objects.get(username=username)
    myProfile = UserProfile.objects.get(user=myUser)
    allUserProfiles = UserProfile.objects.all()
    resultInfos = []

    simTable = STF.gen_sim_table_from_tbq(myProfile)

    myChoiceAnss = gen_table_scq_mcq(Answer.objects.filter(profile=myProfile))
    for up in allUserProfiles:
        if up.user.username == username or up.user.username == 'admin': #except user itself and admin
            continue

        otherChoiceAnss = gen_table_scq_mcq(Answer.objects.filter(profile=up))
        totalWeight = 0

        for myQNum in myChoiceAnss.keys():
            if myQNum in otherChoiceAnss: #if the other users have the same questions with me
                totalWeight += myChoiceAnss[myQNum].calcChoiceWeight(otherChoiceAnss[myQNum])
            if myQNum in simTable:
                totalWeight += simTable[myQNum][up.user.username]
        if len(myChoiceAnss) > 0:
            resultInfos.append(Resultinfo(up.user.username,totalWeight / len(myChoiceAnss) * 100))
    sr = sorted(resultInfos,key = Resultinfo.getPercent,reverse=True)
    return sr