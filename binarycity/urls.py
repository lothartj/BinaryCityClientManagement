from django.urls import path
from . import views, viewsanalytics, viewschat

urlpatterns = [
    path('', views.index, name='index'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:client_id>/link-contact/<int:contact_id>/', views.link_contact_to_client, name='link_contact_to_client'),
    path('clients/<int:client_id>/unlink-contact/<int:contact_id>/', views.unlink_contact_from_client, name='unlink_contact_from_client'),
    path('client-contacts-analytics/', views.get_client_contacts_analytics, name='client_contacts_analytics'),
    path('contact-clients-analytics/', views.get_contact_clients_analytics, name='contact_clients_analytics'),
    path('ai-analytics-insights/', viewsanalytics.get_ai_analytics_insights, name='ai_analytics_insights'),
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/create/', views.ContactCreateView.as_view(), name='contact_create'),
    path('contacts/<int:pk>/edit/', views.ContactUpdateView.as_view(), name='contact_update'),
    path('contacts/<int:contact_id>/link-client/<int:client_id>/', views.link_client_to_contact, name='link_client_to_contact'),
    path('contacts/<int:contact_id>/unlink-client/<int:client_id>/', views.unlink_client_from_contact, name='unlink_client_from_contact'),
    path('chat/', viewschat.chat, name='chat'),
    path('chat/get_response/', viewschat.get_ai_response, name='get_ai_response'),
    path('chat/clear/', viewschat.clear_conversation, name='clear_conversation'),
]