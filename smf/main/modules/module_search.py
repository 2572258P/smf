
from main.models.models import Question,Answer,UserProfile,InvData,Choice
from .module_common import GetCategoryLabel,GetWeightByPriority
from .module_NLP import NLP



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
    def __init__(self,label,code):
        self.totalScore = 0
        self.score = 0
        self.per = 0
        self.label = label
        self.code = code

    def CalcPercentage(self):
        self.per = round(self.score / self.totalScore * 100,2) if self.totalScore > 0 else 0
        
    def addPoint(self,point):
        self.score += point
        self.per = round(self.score / self.totalScore * 100,2) if self.totalScore > 0 else 0
    def getPer(self):
        return self.per

class SearchEntity:
    def __init__(self):
        self.cat_info = {}

    def addCatTotalScore(self,cat_str,score):
        if cat_str not in self.cat_info:
            self.cat_info[cat_str] = CategoryInfo(GetCategoryLabel(cat_str),cat_str)
        self.cat_info[cat_str].totalScore += score

    def addCatScore(self,cat_str,score):
        if cat_str not in self.cat_info:
            self.cat_info[cat_str] = CategoryInfo(GetCategoryLabel(cat_str),cat_str)            
        self.cat_info[cat_str].score += score
    
    def sortCategory(self):
        self.cat_info = dict(sorted(self.cat_info.items(),key = lambda i: i[1].per,reverse=True))

    def getPercent(self):
        return self.percent
    def getAccPoint(self):
        return self.accPoint
    def generateAll(self,other_pf,percent,mp,accPoint,totalPoint):
        self.percent = percent
        self.pf_pk = other_pf.pk
        self.profile_text = ""
        self.QTs = []
        self.Anss = []
        self.opens = []
        self.prios = []
        self.types = []
        self.username = ""
        self.accPoint = accPoint
        self.totalPoint = totalPoint

        profile = UserProfile.objects.filter(pk=self.pf_pk).first()
        if InvData.objects.filter(from_pk=mp.pk,to_pk=other_pf.pk,accepted=True).first() or InvData.objects.filter(from_pk=other_pf.pk,to_pk=mp.pk,accepted=True).first():
            self.username = profile.user.username
        
        if profile and profile.profile_text_open == True:
            self.profile_text = profile.profile_text
        else:
            self.profile_text = "Profile text is not opened."
        
        for q in Question.objects.all():
            ans_models = Answer.objects.filter(question_id=q.pk,profile=profile)
            if not Answer.objects.filter(question_id=q.pk,profile=mp):
                continue
            if ans_models.count() == 0:
                continue
            self.prios.append(q.priority)
            self.QTs.append(q.title)
            self.opens.append(False)
            self.types.append(q.type)
            ans_ls = []

            for am in ans_models:                
                if len(am.answer_text) <= 0: #non-text-based
                    ch = Choice.objects.filter(pk=am.choice_id).first()
                    if ch:
                        ans_ls.append(ch.choice_text)
                else:
                    ans_ls.append(am.answer_text)                
                self.opens[len(self.opens)-1] = am.open_to_others
                    
            self.Anss.append(ans_ls)
        
        for k,v in self.cat_info.items():
            v.CalcPercentage()


def getSeachEntity(my_pf,other_pf,SimDictTable_tbq):
    myQnATable = gen_table_by_answers(Answer.objects.filter(profile=my_pf))
    otherQnATable = gen_table_by_answers(Answer.objects.filter(profile=other_pf))  

    accPoint = 0
    totalPoint = 0
    ose = SearchEntity()
    for myQId in myQnATable.keys():
        qo = Question.objects.filter(pk=myQId).first()
        priorityWeight = GetWeightByPriority(qo.priority) if qo != None else 0
        totalPoint = totalPoint + priorityWeight
        ose.addCatTotalScore(qo.category,priorityWeight)

        score = 0
        if myQId in otherQnATable: #if the other users have the same questions with me
            score = myQnATable[myQId].calcChoiceWeight(otherQnATable[myQId]) * priorityWeight                
        if myQId in SimDictTable_tbq:
            score = SimDictTable_tbq[myQId][other_pf.user.username] * priorityWeight
        accPoint += score        
        ose.addCatScore(qo.category,score)
            
    if len(otherQnATable) > 0 and totalPoint > 0:
        accPoint = round(accPoint,2)
        percent = round(accPoint / totalPoint * 100,2)
        totalPoint = round(totalPoint,2)
        ose.generateAll(other_pf,percent,my_pf,accPoint,totalPoint)
        ose.sortCategory()
        return ose

    return None

