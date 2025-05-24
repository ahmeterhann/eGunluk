from django.contrib import admin
from .models import Diary

# Register your models here.

@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'title', 'content', 'date')

#Ahmet, ahmeterhanergen@gmail.com, manavgat2001