from sentence_transformers import SentenceTransformer, util
from main.models.models import Question,Choice,UserProfile,Answer
import time

def s_to_f(obj):
    return round(float(obj),2)
    
class NLP():
    """
    Purpose of the class
    1. caching the calculated results with similarities
    2. providing utilities for NLP
    """
    words = []
    scores = []
    initialized = False
    model = None
    @staticmethod
    def Init():
        
        if NLP.initialized == True:
            return
        NLP.initialized = True

        NLP.model = SentenceTransformer('all-MiniLM-L6-v2')
        #NLP.model = SentenceTransformer('all-mpnet-base-v2')
        #NLP.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        
        
        for c in Choice.objects.all():
            if c.choice_text in NLP.words:
                continue
            NLP.words.append(c.choice_text)
        NLP.calculate()
    @staticmethod
    def Update():
        updated = False
        words = [ ch.choice_text for ch in Choice.objects.all() ]

        for word in words:
            if word in NLP.words:
                continue
            updated = True
            NLP.words.append(word)
        if updated == True:
            NLP.calculate()

    @staticmethod
    def getScore(word1,word2):
        if word1 not in NLP.words or word2 not in NLP.words:
            return 0
        idx1 = NLP.words.index(word1)
        idx2 = NLP.words.index(word2)
        return s_to_f(NLP.scores[idx1][idx2])

    @staticmethod
    def calculate():
        #Compute embedding for both lists        
        if len(NLP.words) <= 0 or not NLP.model: 
            return
        embeddings1 = NLP.model.encode(NLP.words, convert_to_tensor=True)
        embeddings2 = NLP.model.encode(NLP.words, convert_to_tensor=True)

        #Compute cosine-similarities
        NLP.scores = util.cos_sim(embeddings1, embeddings2)
    @staticmethod
    def calculate_single_similarities(sen1,sen2):
        #Compute embedding for both lists
        embeddings1 = NLP.model.encode([sen1], convert_to_tensor=True)
        embeddings2 = NLP.model.encode([sen2], convert_to_tensor=True)

        #Compute cosine-similarities
        cosine_scores = util.cos_sim(embeddings1, embeddings2)

        return s_to_f(cosine_scores[0][0])
    @staticmethod
    def calculate_similarities(array1,array2):
        #Compute embedding for both lists
        embeddings1 = NLP.model.encode(array1, show_progress_bar=True)
        embeddings2 = NLP.model.encode(array2, show_progress_bar=True)

        #Compute cosine-similarities
        cosine_scores = util.cos_sim(embeddings1, embeddings2)

        return cosine_scores
    @staticmethod
    def gen_sim_dict_from_tbq(myProfile,otherPFs):
        if len(otherPFs) == 0:
            return None
            
        tbqs = Question.objects.filter(type='tbq').exclude(approved=False)
        table = {}
        for tbq in tbqs:            
            myans = Answer.objects.filter(question_id = tbq.id,profile=myProfile).first()
            if myans is None: #if the current account does not have the answer, do not create the table.
                continue
            otherAnsArr = []
            myAnsArr = []
            table[tbq.id] = {}
            myAnsArr.append( myans.answer_text )

            for OUP in otherPFs:
                otherAns = Answer.objects.filter(question_id = tbq.id,profile=OUP).first()
                otherAnsArr.append( otherAns.answer_text if otherAns != None else "")

            print("---- Start NLP Operation -----")
            startTime = time.time()
            
            simResult = NLP.calculate_similarities(myAnsArr,otherAnsArr)
            for i in range(len(otherAnsArr)):
                if len(otherAnsArr[i]) == 0:
                    simResult[0][i] = 0

            print("----- End NLP Operation Time: {}s".format(time.time()-startTime))
            i = 0
            for OUP in otherPFs:
                table[tbq.id][OUP.user.username] = s_to_f(simResult[0][i])
                i += 1        
        return table