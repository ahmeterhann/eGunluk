from django.urls import path
from . import views

app_name = 'frontenddiaryapp' 

urlpatterns = [
    path('', views.home_view, name='anasayfa'),
    path('adddiary/', views.add_diary_view, name='add-diary-view'),
    path('listdiaries/', views.diary_list_view, name='diary-list-view'),
    path('updatediaries/<int:id>/', views.diary_detail_view, name='diary-update-view'),
    path('savediaries/<int:pk>/', views.diary_update_view, name='diary-save-view'),
    path('deletediaries/<int:pk>', views.diary_delete_view, name='diary-delete-view'),
    path('search/', views.search_results_view, name='search-results-view'),
    path('profile/', views.profile_view, name='profile-view'),
    path('profile-readonly/', views.profile_readonly_view, name='profile-readonly-view'),



    

    
]
