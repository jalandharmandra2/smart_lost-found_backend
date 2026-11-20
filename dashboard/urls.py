from django.urls import path
from .views import DashboardStatsView, AdminUsersListView, AdminUserDetailView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('users/', AdminUsersListView.as_view(), name='dashboard-users'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='dashboard-user-detail'),
]
