from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import LostItem
from .serializers import LostItemSerializer
from ai_matching.services import find_and_record_matches_for_lost_item
from ai_matching.models import MatchRecord

class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return (obj.user_id == request.user.id) or request.user.is_staff or (getattr(request.user, 'role', '') == 'ADMINISTRATOR')


class LostItemViewSet(viewsets.ModelViewSet):
    queryset = LostItem.objects.all()
    serializer_class = LostItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['item_name', 'description', 'location', 'colour', 'brand_or_maker']
    ordering_fields = ['created_at', 'date_lost', 'reward_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = LostItem.objects.select_related('user').prefetch_related('images').filter(is_active=True)
        category = self.request.query_params.get('category')
        colour = self.request.query_params.get('colour')
        status_val = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        q = self.request.query_params.get('q')

        if category:
            qs = qs.filter(category=category)
        if colour:
            qs = qs.filter(colour__icontains=colour)
        if status_val:
            qs = qs.filter(status=status_val)
        if date_from:
            qs = qs.filter(date_lost__gte=date_from)
        if date_to:
            qs = qs.filter(date_lost__lte=date_to)
        if q:
            qs = qs.filter(
                Q(item_name__icontains=q) |
                Q(description__icontains=q) |
                Q(location__icontains=q) |
                Q(colour__icontains=q)
            )

        return qs

    def perform_create(self, serializer):
        instance = serializer.save()
        # Trigger real-time AI matching against all active found items
        try:
            find_and_record_matches_for_lost_item(instance)
        except Exception as e:
            # Catch matching errors gracefully so report creation succeeds
            pass

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.status = 'CLOSED'
        instance.save(update_fields=['is_active', 'status'])

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_items(self, request):
        """Retrieve items reported by current user."""
        items = LostItem.objects.filter(user=request.user, is_active=True).prefetch_related('images')
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """Get AI-generated matches for this specific lost item."""
        lost_item = self.get_object()
        from ai_matching.serializers import MatchRecordSerializer
        matches = MatchRecord.objects.filter(lost_item=lost_item).select_related('found_item', 'found_item__user').prefetch_related('found_item__images').order_by('-total_score')
        serializer = MatchRecordSerializer(matches, many=True, context={'request': request})
        return Response(serializer.data)
