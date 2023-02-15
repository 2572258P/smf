from .models.models import UserProfile,Update


def main_cp(request):
    context = {}
    if request.user.is_authenticated:
        mp = UserProfile.objects.filter(user=request.user).first()
        if mp:
            context['has_request'] = True if Update.objects.filter(profile=mp).count() > 0 else False
            context['is_admin'] = mp.admin            
    else:
        context['has_request'] = False
        context['is_admin'] = False        
    return context