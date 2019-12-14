from django.urls import path

from . import views
from .views import ControlPanelView, ConfigFormView, SavingFormView

urlpatterns = [
    path('current/api/data/android', views.get_current_data_from_emotions, name='current_emotions'),
    path('current/api/data/gr_android', views.get_grouped_current_data_from_emotions, name='current_gr_emotions'),
    path('current/api/data/django', views.get_current_data_from_raw_data, name='current_raw_data'),
    path('current/api/data/gr_django', views.get_grouped_current_data_from_raw_data, name='current_gr_raw_data'),
    path('preview/api/data/android', views.get_preview_stats_from_emotions, name='preview_emotions'),
    path('preview/api/data/gr_android', views.get_grouped_preview_stats_from_emotions, name='preview_gr_emotions'),
    path('preview/api/data/django', views.get_preview_stats_from_raw_data, name='preview_raw_data'),
    path('preview/api/data/gr_django', views.get_grouped_preview_stats_from_raw_data, name='preview_gr_raw_data'),
    path('current/', views.current_stats, name='current_stats'),
    path('preview/', views.preview_stats, name='preview'),
    path('about/', views.about, name='about'),
    path('control/', ControlPanelView.as_view(), name='control_panel'),
    path('config/submit', ConfigFormView.as_view(), name='config'),
    path('saving/submit', SavingFormView.as_view(), name='saving'),
    path('', views.index, name='index'),
]
