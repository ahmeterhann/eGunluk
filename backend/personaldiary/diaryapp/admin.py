from django.contrib import admin
from .models import Diary, Profile

# Register your models here.

@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'title', 'content', 'date')

#Ahmet, ahmeterhanergen@gmail.com, manavgat2001

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'age', 'gender', 'birth_date', 'location')