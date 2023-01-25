
import os
import random

# Tell Django where the settings.py module is located
os.environ.setdefault('DJANGO_SETTINGS_MODULE','smf.settings')
import django
import sys

django.setup()

from main.models import Question,Answer,UserProfile,Choice
from django.utils import timezone
import time
from django.contrib.auth.models import User
import pandas as pd
import csv


def generateQuestion(num):
    q = Question(title="Question{}".format(num),pub_date=timezone.now(),type='scq',ctrl_type='radio')
    q.save()
    for i in range(5):
        q.choice_set.create(choice_text="choice {}".format(i+1))



def generate_user(count):
    t = time.localtime()
    current_time = time.strftime("%d%y%m_%H%M%S", t)
    
    for i in range(count):
        try:
            print("progress :{:.0f}%".format((i+1)/(count)*100))
            username = "user_"+current_time+str(i)
            newuser = User.objects.create_user(username=username, password='123456ab!')
            userpf = UserProfile(user=newuser)
            userpf.save()
        except Exception as inst:
            print(inst)

def allocate_random_answer(users):
    for user in users:        
        if user.username == 'admin':
            continue

        profile = UserProfile.objects.get(user=user)        
        anss = Answer.objects.filter(profile = profile)
        anss.delete()
        for q in Question.objects.all():
            if q.type == 'tbq':
                dataset = pd.read_csv("dataset/dataset.csv")
                randIndex = random.randint(0,len(dataset['review/text'])-1)
                text = dataset['review/text'][randIndex][:32]
                print(text)
                a = Answer(answer_text=text,choice_id=-1,profile=profile,question_id=q.pk)
                a.save()
            else:
                cs = Choice.objects.filter(question = q)
                cs_ids = [c.id for c in cs] 
                count = 1 if q.type == 'scq' else len(cs)
                random_count = random.randint(1,count)
                for i in range(random_count):
                    random_id = random.randint(0,len(cs_ids)-1)
                    if random_id < len(cs_ids):
                        a = Answer(choice_id = cs_ids.pop(random_id),profile=profile,question_id=q.pk,answer_text="")
                        a.save()

def generate_questions(filename):        
    with open("./Qs_preset.csv", 'r') as file:        
        csvreader = csv.reader(file)
        NewQ = None
        for row in csvreader:
            r0 = row[0]
            r1 = row[1]            
            if r0 == 'title':
                if r1:
                    print("Started to create - {}".format(r1))
                    NewQ = Question(title=r1,pub_date=timezone.now())
                    NewQ.save()
            elif r0 == 'desc':
                if NewQ and r1:
                    NewQ.desc = r1
                    NewQ.save()
            elif r0 == 'type':
                if NewQ and r1:
                    if r1 == 'scq':
                        NewQ.ctrl_type = 'radio'
                    if r1 == 'mcq':
                        NewQ.ctrl_type = 'checkbox'
                    NewQ.type = r1
                    NewQ.save()
            elif r0 == 'category':
                if NewQ and r1:
                    NewQ.category = r1
                    NewQ.save()
            elif r0 == 'priority':
                if NewQ and r1:
                    NewQ.priority = r1
                    NewQ.save()
            elif r0 == 'match_type':
                if NewQ and r1:
                    NewQ.match_type = r1
                    NewQ.save()
            else:
                if NewQ and r1:                    
                    NewQ.choice_set.create(choice_text=r1)




if __name__ == "__main__":
    cmdlist = {"generate_users":"generate_users",
    "allocate_answers":"allocate_answers",
    "delete_all_users":"delete_all_users",
    "clear_all":"clear_all",
    "gq":"gq"}


    if( len(sys.argv) > 1 ):
        cmd = sys.argv[1]
        if cmd == 'help':
            print(cmdlist)
        if cmd in cmdlist:
            if cmd == cmdlist['gq']:
                generate_questions(sys.argv[2])
            elif cmd == cmdlist['generate_users']:
                generate_user(int(sys.argv[2]))
            elif cmd == cmdlist['allocate_answers']:
                allocate_random_answer(User.objects.all())
            elif cmd == cmdlist['delete_all_users']:
                User.objects.all().exclude(username='admin').delete()
                print('all users have been deleted')
            elif cmd == cmdlist['clear_all']:
                User.objects.all().exclude(username='admin').delete()
                Question.objects.all().delete()
        else:
            print('command is not valid - use help')

#if(sys.argv[1] == 'deldb'):            
#    Question.objects.all().delete()
#if(sys.argv[1] == 'gen'):
    #generate()
#print(sys.argv[1] + " - Finished")
