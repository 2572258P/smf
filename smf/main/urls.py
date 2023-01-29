from django.urls import path,re_path
from main import views

app_name = 'main'

urlpatterns = [
    path('',views.dashboard,name='dashboard'),    
    path('reg/',views.registration,name='registration'),
    path('my_account/',views.my_account,name='my_account'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('find_mates/',views.find_mates,name='find_mates'),    
    path('question_management/',views.question_management,name='question_management'),
    path('question_creator/',views.question_creator,name='question_creator'),
    path('question_creator/<str:question_type>/',views.question_creator,name='question_creator'),
    re_path(r'^start_searching/(?P<userId>\w+)',views.start_searching,name='start_searching'),
    path('login_requirement/',views.login_requirement,name='login_requirement'),
    path('my_mates/',views.my_mates,name='my_mates'),
    re_path(r'^list_result/(?P<userId>\w+)',views.list_result,name='list_result'),
    path('sign_in_page/',views.sign_in_page,name='sign_in_page'),
    path('about_us/',views.dashboard,name='about_us'),
]
