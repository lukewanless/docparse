from django.urls import path

from . import views

urlpatterns = [
    path('generate/', views.generate, name='generate'),
    path('error-handler/', views.error_handler, name='error_handler'),
    path('', views.upload, name='upload'),
]

