from .models import Question,Answer,UserProfile
from collections import defaultdict
from django.contrib.auth.models import User


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
            print("user:{} questionid:{} answer:{}".format(op.user.username,ma.question_id,ma.choice_id))
            matchedCount += len(matchedAnss)
    
    return int((matchedCount / totalCount) * 100)


def handle_search_result(username):
    myUser = User.objects.get(username=username)
    myProfile = UserProfile.objects.get(user=myUser)

    allUserProfiles = UserProfile.objects.all()
    
    resultInfos = []
    

    myAnss = Answer.objects.filter(profile=myProfile).exclude(choice_id=-1)

    for up in allUserProfiles:
        if up.user.username == username or up.user.username == 'admin':
            continue
        otherAnss = Answer.objects.filter(profile=up)
        resultInfos.append(resultinfo(up.user.username, getPercentWithAnswers(myProfile,up,myAnss,otherAnss)))

    sr = sorted(resultInfos,key = resultinfo.getPercent,reverse=True)    
    return sr