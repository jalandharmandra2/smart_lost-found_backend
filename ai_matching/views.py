from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q
from .models import MatchRecord
from .serializers import MatchRecordSerializer, MatchResponseSerializer
from .services import find_and_record_matches_for_lost_item, find_and_record_matches_for_found_item
from lost_items.models import LostItem
from found_items.models import FoundItem

class MatchRecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MatchRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', '') == 'ADMINISTRATOR':
            qs = MatchRecord.objects.all()
        else:
            # Matches where the user is either the lost item owner or found item reporter
            qs = MatchRecord.objects.filter(
                Q(lost_item__user=user) | Q(found_item__user=user)
            )

        match_label = self.request.query_params.get('match_label')
        lost_id = self.request.query_params.get('lost_item_id')
        found_id = self.request.query_params.get('found_item_id')

        if match_label:
            qs = qs.filter(match_label=match_label.upper())
        if lost_id:
            qs = qs.filter(lost_item_id=lost_id)
        if found_id:
            qs = qs.filter(found_item_id=found_id)

        return qs.select_related('lost_item', 'lost_item__user', 'found_item', 'found_item__user').prefetch_related('lost_item__images', 'found_item__images').order_by('-total_score')

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """
        Manually trigger AI matching inference for all active items or a specified item.
        """
        lost_item_id = request.data.get('lost_item_id')
        found_item_id = request.data.get('found_item_id')

        matched_count = 0
        if lost_item_id:
            lost_item = LostItem.objects.filter(id=lost_item_id, is_active=True).first()
            if not lost_item:
                return Response({'error': 'Lost item not found.'}, status=status.HTTP_404_NOT_FOUND)
            matches = find_and_record_matches_for_lost_item(lost_item)
            matched_count = len(matches)
        elif found_item_id:
            found_item = FoundItem.objects.filter(id=found_item_id, is_active=True).first()
            if not found_item:
                return Response({'error': 'Found item not found.'}, status=status.HTTP_404_NOT_FOUND)
            matches = find_and_record_matches_for_found_item(found_item)
            matched_count = len(matches)
        else:
            # Recalculate for all active items
            for lost in LostItem.objects.filter(is_active=True):
                matches = find_and_record_matches_for_lost_item(lost)
                matched_count += len(matches)

        return Response({
            'message': f'AI matching completed successfully. {matched_count} potential matches recorded or updated.',
            'matches_found': matched_count
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        """
        Allow user to respond to a potential match (viewed, initiate claim, dismiss).
        """
        match_record = self.get_object()
        serializer = MatchResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match_record.status = serializer.validated_data['status']
        if serializer.validated_data.get('notes'):
            match_record.response_notes = serializer.validated_data['notes']
        match_record.save(update_fields=['status', 'response_notes', 'updated_at'])

        return Response({
            'message': f"Match status updated to {match_record.status}.",
            'match': MatchRecordSerializer(match_record, context={'request': request}).data
        })
