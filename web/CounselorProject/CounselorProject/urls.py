from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('start_transcription/', views.start_transcription, name='start_transcription'),
    path('stop_transcription/', views.stop_transcription, name='stop_transcription'),
]