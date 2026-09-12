from django.urls import path

from . import views

app_name = 'formations'

urlpatterns = [
    path('<slug:slug>/', views.detail, name='detail'),
]
