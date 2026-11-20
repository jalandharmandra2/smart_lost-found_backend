from django.urls import path
from .views import LocationPointListView, NearbyItemsView

urlpatterns = [
    path('', LocationPointListView.as_view(), name='location-list'),
    path('nearby/', NearbyItemsView.as_view(), name='items-nearby'),
]
