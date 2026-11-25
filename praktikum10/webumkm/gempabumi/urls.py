from django.urls import path
from . import views

urlpatterns = [
    path('gempabumi/', views.gempaterkini, name='gempaterkini'),
]