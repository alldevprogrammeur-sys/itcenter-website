from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    # Root of the site handled by core.welcome
    path("", views.welcome, name="welcome"),
]
