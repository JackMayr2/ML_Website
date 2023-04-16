from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.HomeView.as_view()),


]
