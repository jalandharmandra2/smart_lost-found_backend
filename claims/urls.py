from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClaimRequestViewSet

router = DefaultRouter()
router.register(r'', ClaimRequestViewSet, basename='claim')

urlpatterns = [
    path('', include(router.urls)),
]
