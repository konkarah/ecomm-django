from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('protected/', views.protected_view, name='protected'),
    path('create/', views.create_resource, name='create_resource'),
    path('userinfo/', views.UserInfoView.as_view(), name='userinfo'),

]

