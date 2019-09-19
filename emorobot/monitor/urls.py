from django.urls import path

from . import views

urlpatterns = [
    path('api/data/', views.get_data, name='data'),
    path('api/chart/data/', views.ChartData.as_view(), name='chart'),
    path('', views.index, name='index'),
]
