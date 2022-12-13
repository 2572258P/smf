from .models import Question,Answer,UserProfile
from collections import defaultdict
from django.contrib.auth.models import User

from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')



def calculate_similarities(sen1,sen2):
    #Compute embedding for both lists
    embeddings1 = model.encode([sen1], convert_to_tensor=True)
    embeddings2 = model.encode([sen2], convert_to_tensor=True)

    #Compute cosine-similarities
    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    return cosine_scores[0][0]


class ansdata():
    def __init__(self):
        self.choices = []
        self.text = ""
    def addChoice(self,choice):
        if choice != -1:
            self.choices.append(choice)
    def addText(self,text):
        if text != '' and text != None:
            self.text = text
    def calc(self,otherAns):
        matchedCount = 0
        for mc in self.choices:
            if mc in otherAns.choices:
                matchedCount += 1
        if matchedCount > 0: #When a question type is scq or mcq
            return matchedCount / len(self.choices)
        elif self.text != None and self.text != "":
            return calculate_similarities(self.text,otherAns.text)
        else:
            return 0


class resultinfo():
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

def convertToAnsdata(ansQuery):
    result = {}
    for ans in ansQuery:
        if ans.question_id not in result:
            result[ans.question_id] = ansdata()
        result[ans.question_id].addChoice(ans.choice_id)
        result[ans.question_id].addText(ans.answer_text)
    return result

def handle_search_result(username):
    myUser = User.objects.get(username=username)
    myProfile = UserProfile.objects.get(user=myUser)
    allUserProfiles = UserProfile.objects.all()    
    print(" ----- ----- ")
    print(allUserProfiles)
    resultInfos = []

    myAnss = convertToAnsdata(Answer.objects.filter(profile=myProfile))
    for up in allUserProfiles:
        if up.user.username == username or up.user.username == 'admin':
            continue

        otherAnss = convertToAnsdata(Answer.objects.filter(profile=up))
        totalWeight = 0        
        for mk in myAnss.keys():
            if mk in otherAnss:
                totalWeight += myAnss[mk].calc(otherAnss[mk])
        resultInfos.append(resultinfo(up.user.username,totalWeight / len(myAnss) * 100))
    sr = sorted(resultInfos,key = resultinfo.getPercent,reverse=True)
    return sr