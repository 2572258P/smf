from django.urls import path,re_path
app_name = 'main'

from main.views import view_Home,view_Signin,view_Base,view_Registration,view_MyAccount,\
view_FindMates,view_QuestionEditor,view_QuestionSubmit,view_SearchStart,view_SearchResult,\
view_MyMates,view_SigninRequirement,view_AboutUs,view_ProcessCommonLoading,view_ProcessCommonResult

from django.views.generic.base import RedirectView


urlpatterns = [
    path('',view_Home.loadpage,name='home'),
    path('page_signin/',view_Signin.loadpage,name='page_signin'),
    path('signin/',view_Base.signin,name='login'),
    path('signout/',view_Base.signout,name='signout'),
    path('page_registration/',view_Registration.loadpage,name='page_registration'),
    path('page_myaccount/',view_MyAccount.loadpage,name='page_myaccount'),
    path('page_mymates/',view_MyMates.loadpage,name='page_mymates'),
    path('page_findmates/',view_FindMates.loadpage,name='page_findmates'),
    path('page_question_editor/',view_QuestionEditor.loadpage,name='page_question_editor'),
    path('page_question_submit/',view_QuestionSubmit.loadpage,name='page_question_submit'),
    path('page_question_submit/<str:question_type>/',view_QuestionSubmit.loadpage,name='page_question_submit'),
    re_path(r'^page_search_start/(?P<userId>\w+)',view_SearchStart.loadpage,name='page_search_start'),
    re_path(r'^page_search_result/(?P<username>\w+)',view_SearchResult.loadpage,name='page_search_result'),
    path('about_us/',view_AboutUs.loadpage,name='about_us'),
    path('page_signin_requirement/',view_SigninRequirement.loadpage,name='page_signin_requirement'),
    path('loading/',view_ProcessCommonLoading.loadpage,name='loading'),
    path('result/',view_ProcessCommonResult.loadpage,name='result'),
    

]
