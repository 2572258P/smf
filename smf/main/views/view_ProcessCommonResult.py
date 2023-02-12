from django.http import HttpResponse,JsonResponse
from django.shortcuts import render

#    print(request.session['temp_session'])
def loadpage(request):
    context = {}
    context['main_msg'] = request.session.get('main_msg','')
    context['sub_msg'] = request.session.get('sub_msg','')
    

    return render(request,'process_common_result.html',context)