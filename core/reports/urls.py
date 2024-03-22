from django.urls import path 
from . import views

urlpatterns = [
    path('', views.list_website_reports, name='list_website_reports'),
    path('show-website-report/<int:report_id>/', views.show_website_report, name='show_website_report'),
    path('delete-website-report/<int:report_id>/', views.delete_website_report, name='delete_website_report'),
]