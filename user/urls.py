from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/', views.register, name='user-register'),
    path('profile/<int:pk>/', views.profile, name='user-profile'),
    path('profile_update/<int:pk>/', views.profile_update, name='user-profile_update'),
    

    path('user-login', auth_views.LoginView.as_view(template_name='user/login.html'),
          name='user-login'),
          
    path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'), 
         name='user-logout'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'), 
    name='password_reset'),
    
    #the uidb64 and token is a security feature..
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),
    name='password_reset_confirm'),
    
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
    name='password_reset_done'),

    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
    name='password_reset_complete'),



] 
