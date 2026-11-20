from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoundItemViewSet

router = DefaultRouter()
router.register(r'', FoundItemViewSet, basename='found-item')

urlpatterns = [
    path('', include(router.urls)),
]
