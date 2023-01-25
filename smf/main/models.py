import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



# User Info
class UserProfile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    profile_text = models.CharField(max_length=500)
    email = models.EmailField(max_length=254)
    admin = models.BooleanField(default=False)
    profile_text_open = models.BooleanField(default=True)
    def __str__(self):
        return self.user.username

class LastAccUser(models.Model): #temporary for testing - will be removed after completing user session authentication
    lastUser = models.CharField(max_length=32)
    def __str__(self):
        return self.lastUser

# Create your models here.
class Question(models.Model):
    def __str__(self):
        return self.title
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)        

    approved = models.BooleanField(default=True)

    type = models.CharField(max_length=32) #SCQ / MCQ / Text-based ...
    category = models.CharField(max_length=32) # Common Type / User registered / Details ...
    ctrl_type = models.CharField(max_length=16)
    title = models.CharField(max_length=256)
    desc = models.CharField(max_length=512)

    pub_date = models.DateTimeField('date published')
    priority = models.CharField(max_length=8) 
    match_type = models.CharField(max_length=8)

class Choice(models.Model):
    def __str__(self):
        return self.choice_text
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

class Answer(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    question_id = models.IntegerField(default=-1)
    choice_id =  models.IntegerField(default=-1)
    answer_text = models.CharField(max_length=1000)

class QuestionVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)    
    username = models.CharField(max_length=64)
    vote_val = models.IntegerField(default=0)

    
