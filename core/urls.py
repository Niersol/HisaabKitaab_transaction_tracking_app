from django.urls import path
from core.views import *
app_name = 'core'
urlpatterns = [
    path('login/',login_page,name='login-page'),
    path('logout/',logout_user,name='logout'),
    path('user_login/',login_user,name='login-user'),
    path("users/", users_list,name = 'user-list'),
    path('save_user',save_user,name='save-user'),
    path('manage_user',manage_user,name='manage-user'),
    path('manage_user/<int:pk>',manage_user,name='manage-user-pk'),
    path('delete_user/<int:pk>',delete_user,name='delete-user'),
]