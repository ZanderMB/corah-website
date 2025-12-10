from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'events'

urlpatterns = [
    # Path for the list of events (e.g., /events/)
    path("", views.event_list_view, name='event_list'),

    # Path for creating an event (e.g., /events/create/)
    path('create/', views.create_event_view, name='create_event'),

    # Path for a single event's detail page (e.g., /events/2/)
    path('<int:event_id>/', views.event_detail_view, name='event_detail'),

    # Path for registering for an event (e.g., /events/2/register/)
    path('<int:event_id>/register/', views.register_view, name='event_register'),

    # Path for updating an event (e.g., /events/2/update/)
    path('<int:event_id>/update/', views.event_update_view, name='event_form'),

    # Path for deleting an event (e.g., /events/2/delete/)
    path('<int:event_id>/delete/', views.event_delete_view, name='event_delete'),
    
    # Path for registration success (e.g., /events/2/register/success/)
    path('<int:event_id>/register/success/', views.register_success_view, name='register_success'),
]