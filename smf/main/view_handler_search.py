from .models import Question,Answer,UserProfile,STF,Choice
from collections import defaultdict
from django.contrib.auth.models import User

class Ansdata():
    def __init__(self):
        self.choices = []
        self.text = ""
    def addChoice(self,choice):
        if choice != -1:
            self.choices.append(choice)
    def addText(self,text):
        if text != '' and text != None:
            self.text = text
    
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

def convertToAnsdata(ansQuery):
    result = {}
    for ans in ansQuery:
        if ans.question_id not in result:
            result[ans.question_id] = Ansdata()
        result[ans.question_id].addChoice(ans.choice_id)
        result[ans.question_id].addText(ans.answer_text)
    return result


def getSimTableFromTBQ(myProfile):
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
        print(myTextAns,otherTextAns)
        simResult = STF.calculate_similarities(myTextAns,otherTextAns)
        i = 0
        for oun in otherUserNames:
            table[tbq.id][oun] = simResult[0][i]
            i += 1
    return table

def handle_search_result(username):
    myUser = User.objects.get(username=username)
    myProfile = UserProfile.objects.get(user=myUser)
    allUserProfiles = UserProfile.objects.all()
    resultInfos = []

    print(" ----- ----- ")
    simTable = getSimTableFromTBQ(myProfile)
    print(simTable)

    myAnss = convertToAnsdata(Answer.objects.filter(profile=myProfile))
    for up in allUserProfiles:
        if up.user.username == username or up.user.username == 'admin': #except user itself and admin
            continue

        otherAnss = convertToAnsdata(Answer.objects.filter(profile=up))
        totalWeight = 0

        for myQNum in myAnss.keys():
            if myQNum in otherAnss: #if the other users have the same questions with me
                totalWeight += myAnss[myQNum].calcChoiceWeight(otherAnss[myQNum])
            if myQNum in simTable:
                totalWeight += simTable[myQNum][up.user.username]
        
        resultInfos.append(Resultinfo(up.user.username,totalWeight / len(myAnss) * 100))
    sr = sorted(resultInfos,key = Resultinfo.getPercent,reverse=True)
    return sr