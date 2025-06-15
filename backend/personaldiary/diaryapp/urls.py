from django.urls import path
from .views import RegisterView, LoginView, DiaryListCreateView, DiaryRetrieveUpdateDestroyView, DiarySearchView
 

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/diaries/', DiaryListCreateView.as_view(), name='diary-list-create'),
    path('api/diaries/<int:pk>/', DiaryRetrieveUpdateDestroyView.as_view(), name='diary-detail'),
    path('api/diaries/search/', DiarySearchView.as_view(), name='diary-search'),

]

