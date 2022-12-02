from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [    
    path('',views.dashboard,name='dashboard'),
    path('<int:question_id>/',views.detail,name='detail'),
    path('<int:question_id>/results/',views.results,name='results'),
    path('<int:question_id>/vote/',views.vote,name='vote'),
    path('reg/',views.registration,name='registration'),
    path('data_management/',views.data_management,name='data_management'),
    path('search_result/',views.search_reslt,name='search_result'),
    path('question_creator/',views.question_creator,name='question_creator'),
    path('test/',views.test,name='test'),


]
