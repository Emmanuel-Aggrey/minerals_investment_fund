from django.urls import path
from . import views


app_name = "visitor"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_visitor, name='register_visitor'),
    path('reports/', views.reports, name='reports'),
    path('reports/pdf/', views.export_pdf, name='export_pdf'),
    path('reports/excel/', views.export_excel, name='export_excel'),
    path('confirm/<int:pk>/', views.visitor_confirm, name='visitor_confirm'),
    path('visitor/<int:pk>/', views.visitor_detail, name='visitor_detail'),
    path('visitor/<int:pk>/exit/', views.record_exit, name='record_exit'),
]
