from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import LocationPoint
from .serializers import LocationPointSerializer
from .utils import calculate_haversine_distance
from lost_items.models import LostItem
from found_items.models import FoundItem

class LocationPointListView(generics.ListCreateAPIView):
    queryset = LocationPoint.objects.all()
    serializer_class = LocationPointSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class NearbyItemsView(APIView):
    """
    Search lost and found items geographically within a specified radius (km).
    Parameters:
      lat: float (required)
      lng: float (required)
      radius: float (optional, default 25 km)
      item_type: 'all' | 'lost' | 'found' (default 'all')
      category: string (optional)
      q: search query (optional)
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 25.0))
        item_type = request.query_params.get('item_type', 'all').lower()
        category = request.query_params.get('category')
        q = request.query_params.get('q')

        if not lat or not lng:
            # Fallback to returning all geotagged active items if user hasn't granted location
            user_lat, user_lng = None, None
        else:
            try:
                user_lat = float(lat)
                user_lng = float(lng)
            except ValueError:
                return Response({'error': 'Invalid lat or lng coordinate values.'}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        # 1. Fetch Lost Items with coordinates
        if item_type in ['all', 'lost']:
            lost_qs = LostItem.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False).prefetch_related('images')
            if category:
                lost_qs = lost_qs.filter(category=category)
            if q:
                lost_qs = lost_qs.filter(item_name__icontains=q)

            for item in lost_qs:
                dist = calculate_haversine_distance(user_lat, user_lng, item.latitude, item.longitude) if user_lat is not None else None
                if dist is None or dist <= radius:
                    primary_img = item.images.filter(is_primary=True).first() or item.images.first()
                    results.append({
                        'id': item.id,
                        'type': 'lost',
                        'item_name': item.item_name,
                        'category': item.category,
                        'category_display': item.get_category_display(),
                        'colour': item.colour,
                        'date': str(item.date_lost),
                        'location': item.location,
                        'latitude': float(item.latitude),
                        'longitude': float(item.longitude),
                        'distance_km': dist,
                        'image_url': request.build_absolute_uri(primary_img.image.url) if primary_img and primary_img.image else None,
                        'status': item.status
                    })

        # 2. Fetch Found Items with coordinates
        if item_type in ['all', 'found']:
            found_qs = FoundItem.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False).prefetch_related('images')
            if category:
                found_qs = found_qs.filter(category=category)
            if q:
                found_qs = found_qs.filter(item_name__icontains=q)

            for item in found_qs:
                dist = calculate_haversine_distance(user_lat, user_lng, item.latitude, item.longitude) if user_lat is not None else None
                if dist is None or dist <= radius:
                    primary_img = item.images.filter(is_primary=True).first() or item.images.first()
                    results.append({
                        'id': item.id,
                        'type': 'found',
                        'item_name': item.item_name,
                        'category': item.category,
                        'category_display': item.get_category_display(),
                        'colour': item.colour,
                        'date': str(item.date_found),
                        'location': item.found_location,
                        'latitude': float(item.latitude),
                        'longitude': float(item.longitude),
                        'distance_km': dist,
                        'image_url': request.build_absolute_uri(primary_img.image.url) if primary_img and primary_img.image else None,
                        'status': item.status
                    })

        # Sort by proximity if distance is available
        if user_lat is not None:
            results.sort(key=lambda x: x['distance_km'] if x['distance_km'] is not None else 999999)

        return Response({
            'count': len(results),
            'radius_km': radius,
            'items': results
        })
