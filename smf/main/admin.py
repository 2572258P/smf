from django.contrib import admin

from .models import Question
from .models import Choice

admin.site.register(Question)
admin.site.register(Choice)
# Register your models here.

from main.models import UserProfile
admin.site.register(UserProfile)