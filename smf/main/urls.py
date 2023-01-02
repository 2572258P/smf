from django.urls import path,re_path
from main import views

app_name = 'main'

urlpatterns = [    
    path('',views.dashboard,name='dashboard'),
    path('reg/',views.registration,name='registration'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('data_management/',views.data_management,name='data_management'),    
    path('question_management/',views.question_management,name='question_management'),
    path('question_creator/',views.question_creator,name='question_creator'),
    path('question_creator/<str:question_type>/',views.question_creator,name='question_creator'),    
    re_path(r'^search_result/(?P<userId>\w+)',views.search_result,name='search_result'),    
    
]
