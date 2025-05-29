from django.urls import path
from . import views

app_name = 'frontenddiaryapp' 

urlpatterns = [
    path('', views.home_view, name='anasayfa'),
    path('adddiary/', views.add_diary_view, name='add-diary-view'),
    path('listdiaries/', views.diary_list_view, name='diary-list-view'),
    path('updatediaries/<int:id>/', views.diary_detail_view, name='diary-update-view'),

    

    
]
