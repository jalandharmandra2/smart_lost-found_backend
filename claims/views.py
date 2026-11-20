from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import ClaimRequest
from .serializers import ClaimRequestSerializer, ClaimStatusUpdateSerializer
from notifications.services import notify_claim_status_updated

class ClaimRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', '') == 'ADMINISTRATOR':
            return ClaimRequest.objects.all().select_related('claimant', 'found_item', 'lost_item', 'found_item__user').order_by('-created_at')

        # General users / finders only see claims they submitted or claims on items they reported found
        return ClaimRequest.objects.filter(
            Q(claimant=user) | Q(found_item__user=user)
        ).select_related('claimant', 'found_item', 'lost_item', 'found_item__user').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(claimant=self.request.user)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """
        Update the status of a claim (Accept, Reject, Dispute, or Complete).
        Authorized for the Item Finder or Platform Administrators.
        """
        claim = self.get_object()
        user = request.user
        is_finder = (claim.found_item.user_id == user.id)
        is_admin = user.is_staff or (getattr(user, 'role', '') == 'ADMINISTRATOR')

        if not (is_finder or is_admin):
            return Response(
                {'error': 'Only the item finder or an administrator can update claim status.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ClaimStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('response_notes', '')

        claim.status = new_status
        if is_finder:
            claim.finder_response = notes
        if is_admin:
            claim.admin_notes = notes
            claim.reviewed_by = user

        claim.save()

        # Update item status if approved or completed
        if new_status in ['APPROVED', 'COMPLETED']:
            claim.found_item.status = 'RECOVERED' if new_status == 'COMPLETED' else 'CLAIM_PENDING'
            claim.found_item.save(update_fields=['status'])
            if claim.lost_item:
                claim.lost_item.status = 'RECOVERED' if new_status == 'COMPLETED' else 'MATCHED'
                claim.lost_item.save(update_fields=['status'])

        # Notify claimant of status change
        try:
            notify_claim_status_updated(claim)
        except Exception:
            pass

        return Response({
            'message': f"Claim status updated to '{claim.get_status_display()}'.",
            'claim': ClaimRequestSerializer(claim, context={'request': request}).data
        })
