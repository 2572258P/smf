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
    user = models.OneToOneField(User,on_delete=models.CASCADE)
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