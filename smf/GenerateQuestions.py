
import os
import random

# Tell Django where the settings.py module is located
os.environ.setdefault('DJANGO_SETTINGS_MODULE','smf.settings')
import django

django.setup()

from main.models import Question
from django.utils import timezone

def generateQuestion(num):
    q = Question(question_text="question{}".format(num),pub_date=timezone.now())
    q.save()
    for i in range(5):
        q.choice_set.create(choice_text="choice {}".format(i+1))


def generate():
    print("Start")
    for i in range(0,10):
        generateQuestion(i+1)
    print("End")

if __name__ == "__main__":
    generate()