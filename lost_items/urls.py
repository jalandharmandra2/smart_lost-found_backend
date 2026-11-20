from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LostItemViewSet

router = DefaultRouter()
router.register(r'', LostItemViewSet, basename='lost-item')

urlpatterns = [
    path('', include(router.urls)),
]
