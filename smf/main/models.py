import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

"""
Tips
Question.objects.filter
ex1) Question.objects.filter(id=1) 
ex2) Question.objects.filter(question_text__startswith='What')
"""



# User Info
class UserProfile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    profile_text = models.CharField(max_length=500)
    def __str__(self):
        return self.user.username

class LastAccUser(models.Model): #temporary for testing - will be removed after completing user session authentication
    lastUser = models.CharField(max_length=32)
    def __str__(self):
        return self.lastUser

# Create your models here.
class Question(models.Model):
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    type = models.CharField(max_length=32)
    ctrl_type = models.CharField(max_length=16)
    question_text = models.CharField(max_length=200)    
    pub_date = models.DateTimeField('date published')

class Choice(models.Model):
    def __str__(self):
        return self.choice_text
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)    
    votes = models.IntegerField(default=0)

class Answer(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    question_id = models.IntegerField(default=-1)
    choice_id =  models.IntegerField(default=-1)
    answer_text = models.CharField(max_length=1000)


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
        for c in Choice.objects.all():
            if c.choice_text in STF.words:
                continue
            STF.words.append(c.choice_text)
        STF.calculate()
    @staticmethod
    def Update(words):
        updated = False
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
        embeddings1 = STF.model.encode(array1, convert_to_tensor=True)
        embeddings2 = STF.model.encode(array2, convert_to_tensor=True)

        #Compute cosine-similarities
        cosine_scores = util.cos_sim(embeddings1, embeddings2)

        return cosine_scores