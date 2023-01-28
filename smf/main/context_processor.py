from .models import UserProfile


def main_cp(request):
    context = {}
    if request.user.is_authenticated:
        mypf = UserProfile.objects.filter(user=request.user).first()
        if mypf:
            context['has_request'] = mypf.has_request
    else:
        context['has_request'] = False
    return context