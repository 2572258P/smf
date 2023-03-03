
import os
import random

# Tell Django where the settings.py module is located
os.environ.setdefault('DJANGO_SETTINGS_MODULE','smf.settings')
import django
import sys

django.setup()

from main.models.models import Question,Answer,UserProfile,Choice
from django.utils import timezone
import time
from django.contrib.auth.models import User
#import pandas as pd
import csv


def generateQuestion(num):
    q = Question(title="Question{}".format(num),pub_date=timezone.now(),type='scq',ctrl_type='radio')
    q.save()
    for i in range(5):
        q.choice_set.create(choice_text="choice {}".format(i+1))

def generate_users_with_answers(level,count):
    for ui in range(count):
        #Create an account
        username = "user_{}_{}".format(level,User.objects.count())
        newuser = User.objects.create_user(username=username, password='123456ab!')
        userpf = UserProfile(user=newuser)
        userpf.email = "2572258p@gmail.com"
        userpf.save()
        #Assign Questions
        for q in Question.objects.all():
            tex_ans = ''
            text_ans_list = []
            if q.type == 'tbq':
                if q.gen_key == 'c1':
                    text_ans_list.append("Hi my friend!")
                    text_ans_list.append("I like to study in the library.")
                    text_ans_list.append("What do you want to study together?")
                    text_ans_list.append("Which course do you have struggles?")
                    text_ans_list.append("Hello? How are you today?")
                if q.gen_key == 'p1':
                    text_ans_list.append("When I won Nobel peace prize")
                    text_ans_list.append("The childhood when my sister bought me a book.")
                    text_ans_list.append("I met my first love.")
                    text_ans_list.append("Always been miserable.")
                    text_ans_list.append("I'm happy with every moments.")
                if q.gen_key == 'p2':
                    text_ans_list.append(random.randint(1,100))                    
                if q.gen_key == 'p3':
                    text_ans_list.append("I should have had tons of milk about to be taller.")
                    text_ans_list.append("I shouldn't have dropped my piano lessons")
                    text_ans_list.append("I should have asked questions to teachears more.")
                    text_ans_list.append("Raising my painting skills.")
                    text_ans_list.append("I don't know honestly.")
                    text_ans_list.append("What do you want to do?")
                    print()
                if q.gen_key == 'p4':
                    text_ans_list.append("Absolutely, computing programming skills")
                    text_ans_list.append("Predicting lottery numbers")
                    text_ans_list.append("Understanding knowledge completely at the first attempt.")
                    text_ans_list.append("Turn A4 papers into money")
                    text_ans_list.append("Shooting fireballs to the men who I hate")
                    text_ans_list.append("Travelling space wihout a spaceship")
                    print()
                if q.gen_key == 'p5':
                    text_ans_list.append("Waking up ealier than now.")
                    text_ans_list.append("Eating junk foods all day")
                    text_ans_list.append("I will spend more time with my family.")
                    text_ans_list.append("Nothing will be changed, and I wait for my death in a calm.")
                    text_ans_list.append("Spending more money for me")                    
                if q.gen_key == 'p6':
                    text_ans_list.append("The date when I die")
                    text_ans_list.append("When I can travel to the space.")
                    text_ans_list.append("Who is my life partner?")
                    text_ans_list.append("Do I have my PhD degree?")
                    text_ans_list.append("What is my salary level?")

                if len(text_ans_list) > 0:
                    index = random.randint(0,len(text_ans_list)-1)
                    text = text_ans_list[index]
                    a = Answer(profile=userpf,question_id=q.pk,answer_text=text,open_to_others=True)
                    a.save()
            else:
                if q.category == 'cd':
                    cs = Choice.objects.filter(question = q)
                    min = 1
                    if q.type == 'scq':
                        max = 1
                    else:
                        min = int(len(cs)/2)
                        max = min + random.randint(0,len(cs)-min)

                    random_count = 0
                    if level == 1 and q.gen_key == 'courses_lv1':
                        random_count = random.randint(min,max)
                    if level == 2 and q.gen_key == 'courses_lv2':
                        random_count = random.randint(min,max)
                    if level == 3 and q.gen_key == 'courses_lv3':
                        random_count = random.randint(min,max)
                    if level == 4 and q.gen_key == 'courses_lv4':
                        random_count = random.randint(min,max)
                    if level == 5 and q.gen_key == 'courses_lv5':
                        random_count = random.randint(min,max)

                    cs_ids = [c.id for c in cs] 
                    for i in range(random_count):                        
                        random_id = random.randint(0,len(cs_ids)-1)
                        if random_id < len(cs_ids):
                            a = Answer(choice_id = cs_ids.pop(random_id),profile=userpf,question_id=q.pk,answer_text="",open_to_others=True)
                            a.save()
                else:
                    cs = Choice.objects.filter(question = q)
                    cs_ids = [c.id for c in cs] 
                    count = 1 if q.type == 'scq' else len(cs)
                    random_count = random.randint(1,count)
                    for i in range(random_count):
                        random_id = random.randint(0,len(cs_ids)-1)
                        id = cs_ids[level-1] if q.gen_key == 'wcl' else cs_ids.pop(random_id)
                        if random_id < len(cs_ids):
                            a = Answer(choice_id = id,profile=userpf,question_id=q.pk,answer_text="",open_to_others=True)                            
                            a.save()
        print("finished creating a user level:{} index:{}".format(level,ui))
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
                #dataset = pd.read_csv("dataset/dataset.csv")
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
            elif r0 == 'gen_key':
                if r1:
                    if Question.objects.filter(gen_key=r1).first():
                        print("#the question is already in the database.")
                        NewQ.delete() 
                        NewQ = None
                    else:
                        NewQ.gen_key = r1
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
    "delete_all_questions":"delete_all_questions",
    "generate_questions":"generate_questions"}


    if( len(sys.argv) > 1 ):
        cmd = sys.argv[1]
        if cmd == 'help':
            for v in cmdlist:
                print(v)
        if cmd in cmdlist:
            if cmd == cmdlist['generate_questions']:
                generate_questions('Qs_preset.csv')
            elif cmd == cmdlist['generate_users']:
                #generate_user(int(sys.argv[2]))
                generate_users_with_answers(1,5)
                generate_users_with_answers(2,5)
                generate_users_with_answers(3,5)
                generate_users_with_answers(4,5)
                generate_users_with_answers(5,5)
                """
                generate_users_with_answers(1,5)
                generate_users_with_answers(2,5)
                generate_users_with_answers(3,5)
                generate_users_with_answers(4,5)
                generate_users_with_answers(5,5)
                """
            elif cmd == cmdlist['allocate_answers']:
                allocate_random_answer(User.objects.all())
            elif cmd == cmdlist['delete_all_users']:
                User.objects.all().exclude(username='admin').delete()
                print('all users have been deleted')
            elif cmd == cmdlist['delete_all_questions']:                
                Question.objects.all().delete()
        else:
            print('command is not valid - use help')

#if(sys.argv[1] == 'deldb'):            
#    Question.objects.all().delete()
#if(sys.argv[1] == 'gen'):
    #generate()
#print(sys.argv[1] + " - Finished")
