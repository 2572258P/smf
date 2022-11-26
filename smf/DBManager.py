
import os
import random

# Tell Django where the settings.py module is located
os.environ.setdefault('DJANGO_SETTINGS_MODULE','smf.settings')
import django
import sys

django.setup()

from main.models import Question
from django.utils import timezone

def generateQuestion(num):
    q = Question(question_text="Question{}".format(num),pub_date=timezone.now())
    q.save()
    for i in range(5):
        q.choice_set.create(choice_text="choice {}".format(i+1))


def generate():
    print("Start")
    for i in range(0,2):
        generateQuestion(i+1)
    print("End")

if __name__ == "__main__":
    if( len(sys.argv) > 1 ):
        print(sys.argv[1])
        if(sys.argv[1] == 'del'):            
            Question.objects.all().delete()
        if(sys.argv[1] == 'gen'):
            generate()
        print(sys.argv[1] + " - Finished")
            

        