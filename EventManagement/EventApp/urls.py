from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('home/', views.home, name='homepage'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    path('organizer/', views.organizer, name='organizer'),
    path("p_event/", views.p_event, name="p_event"),
    path("participate/", views.participate, name="participate"),
    
]
