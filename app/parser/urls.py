from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('error-handler/', views.error_handler, name='error_handler'),
    path('upload/', views.upload, name='upload'),
]

