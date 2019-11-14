from django.urls import path

from .views import ControlPanelView, ConfigFormView, SavingFormView
from . import views

urlpatterns = [
    path('api/data/', views.get_data, name='data'),
    path('current/api/data/', views.get_current_data, name='current_data'),
    path('preview/api/data/', views.get_preview_data, name='preview_data'),
    path('api/chart/data/', views.ChartData.as_view(), name='chart'),
    path('current/', views.current_stats, name='current_stats'),
    path('preview/', views.preview_stats, name='preview'),
    path('control/', ControlPanelView.as_view(), name='control_panel'),
    path('config/submit', ConfigFormView.as_view(), name='config'),
    path('saving/submit', SavingFormView.as_view(), name='saving'),
    path('', views.index, name='index'),
]
