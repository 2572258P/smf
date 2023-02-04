

from main.models.models import Question,Answer,UserProfile,InvData,Choice
from .module_common import GetCategoryLabel

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
    def addPoint(self,point):
        self.score += point
        self.per = int(self.score / self.totalScore * 100)



class SearchEntity:
    def __init__(self):
        self.cat_info = {}

    def addCatTotalScore(self,cat_str,score):
        if cat_str not in self.cat_info:
            self.cat_info[cat_str] = CategoryInfo(GetCategoryLabel(cat_str))
        self.cat_info[cat_str].totalScore += score

    def addCatScore(self,cat_str,score):
        if cat_str not in self.cat_info:
            self.cat_info[cat_str] = CategoryInfo(GetCategoryLabel(cat_str))
            
        self.cat_info[cat_str].score += score

    def getPercent(self):
        return self.percent
    def generateAll(self,pk,percent,mp):
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
            if not Answer.objects.filter(question_id=q.pk,profile=mp):
                continue

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
        
        
        for k,v in self.cat_info.items():            
            v.CalcPercentage()