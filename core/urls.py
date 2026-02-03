"""
URL configuration for core app (All Minnesota).
Public and dashboard routes.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Public
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('events/', views.EventsView.as_view(), name='events_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('how-it-works/', views.HowItWorksView.as_view(), name='how_it_works'),
    path('impact/', views.ImpactView.as_view(), name='impact'),
    path('volunteer/', views.VolunteerView.as_view(), name='volunteer'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    # Dashboard (LoginRequiredMixin)
    path('dashboard/', views.AdminDashboardView.as_view(), name='dashboard'),
    path('dashboard/goal/', views.GoalUpdateView.as_view(), name='goal_update'),
    path('dashboard/events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('dashboard/events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('dashboard/events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('dashboard/volunteers/', views.VolunteerListView.as_view(), name='volunteer_list'),
    path('dashboard/contacts/', views.ContactListView.as_view(), name='contact_list'),
    # Tasks & Kanban
    path('dashboard/tasks/', views.KanbanBoardView.as_view(), name='kanban'),
    path('dashboard/tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('dashboard/tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('dashboard/tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
]
