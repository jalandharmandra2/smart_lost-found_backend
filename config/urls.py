from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core Modular API Endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/lost-items/', include('lost_items.urls')),
    path('api/found-items/', include('found_items.urls')),
    path('api/matches/', include('ai_matching.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/items/', include('locations.urls')),  # Provides /api/items/nearby/
    path('api/notifications/', include('notifications.urls')),
    path('api/claims/', include('claims.urls')),
    path('api/dashboard/', include('dashboard.urls')),

    # Swagger / OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
