from django.contrib import admin

from .models import Question,Choice,Answer,UserProfile


admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)
# Register your models here.
admin.site.register(UserProfile)