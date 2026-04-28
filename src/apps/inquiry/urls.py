from django.urls import path
from . import views

urlpatterns = [
    path('api/inquiry/chat/', views.chat_api, name='chat_api'),
    path('api/inquiry/confirm/', views.confirm_completion_api, name='chat_confirm'),
]
