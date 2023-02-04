from django import forms
from main.models import UserProfile
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username','password',)
        
class UserProfileForm(forms.ModelForm):
    profile_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 20, 'rows': 10}))
    class Meta:
        model = UserProfile
        fields = ('profile_text',)
