from django.urls import path

from . import views

urlpatterns = [
    path('api/data/', views.get_data, name='data'),
    path('current/api/data/', views.get_current_data, name='current_data'),
    path('api/chart/data/', views.ChartData.as_view(), name='chart'),
    path('current/', views.current_stats, name='current_stats'),
    path('', views.index, name='index'),
]
