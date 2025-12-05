from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list_view, name='event_list'),
    path('register/<int:event_id>/', views.register_view, name='event_register'),
    path('register/<int:event_id>/success/', views.register_success_view, name='event_register_success'),
    path('create/', views.create_event_view, name='create_event'),
]