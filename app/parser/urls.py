from django.urls import path

from . import views

urlpatterns = [
    path('error-handler/', views.error_handler, name='error_handler'),
    path('', views.upload, name='upload'),
    path('api/call_openai/', views.call_openai_api, name='call_openai_api'),
    path('completed/', views.completed, name='completed'),
    path('save/', views.save, name='save'),
    path('download_docx', views.download_docx, name='download_docx'),
    path('display_uploaded_docx', views.display_uploaded_docx, name='display_uploaded_docx'),
]

