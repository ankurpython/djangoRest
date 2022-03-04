from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

task = DefaultRouter()
task.register('tasks', Tasks, basename='tasks')
task.register('logout', Logout, basename='logout')
urlpatterns = [
    path('', include(task.urls)),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='login'),
    path('token_refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
