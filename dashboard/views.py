from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count
from lost_items.models import LostItem
from found_items.models import FoundItem
from ai_matching.models import MatchRecord
from claims.models import ClaimRequest
from accounts.serializers import UserProfileSerializer
from .models import AdminAuditLog

User = get_user_model()

class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.is_staff or getattr(request.user, 'role', '') == 'ADMINISTRATOR')
        )


class DashboardStatsView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        total_users = User.objects.count()
        total_lost = LostItem.objects.count()
        total_found = FoundItem.objects.count()
        total_matches = MatchRecord.objects.count()
        high_matches = MatchRecord.objects.filter(match_label='HIGH').count()
        
        pending_claims = ClaimRequest.objects.filter(status='PENDING').count()
        approved_claims = ClaimRequest.objects.filter(status='APPROVED').count()
        rejected_claims = ClaimRequest.objects.filter(status='REJECTED').count()
        disputed_claims = ClaimRequest.objects.filter(status='DISPUTED').count()
        completed_claims = ClaimRequest.objects.filter(status='COMPLETED').count()

        recovered_lost = LostItem.objects.filter(status='RECOVERED').count()
        recovered_found = FoundItem.objects.filter(status='RECOVERED').count()
        total_recovered = recovered_lost + recovered_found + completed_claims

        # Category distribution across both lost and found
        lost_categories = list(LostItem.objects.values('category').annotate(count=Count('id')).order_by('-count')[:5])
        found_categories = list(FoundItem.objects.values('category').annotate(count=Count('id')).order_by('-count')[:5])

        # Recent activities
        recent_claims = list(ClaimRequest.objects.select_related('claimant', 'found_item').order_by('-created_at')[:5].values(
            'id', 'claimant__username', 'found_item__item_name', 'status', 'created_at'
        ))
        recent_matches = list(MatchRecord.objects.select_related('lost_item', 'found_item').order_by('-created_at')[:5].values(
            'id', 'lost_item__item_name', 'found_item__item_name', 'total_score', 'match_label', 'created_at'
        ))

        return Response({
            'overview': {
                'total_users': total_users,
                'total_lost_items': total_lost,
                'total_found_items': total_found,
                'total_matches': total_matches,
                'high_matches': high_matches,
                'pending_claims': pending_claims,
                'approved_claims': approved_claims,
                'rejected_claims': rejected_claims,
                'disputed_claims': disputed_claims,
                'recovered_items': total_recovered,
            },
            'charts': {
                'lost_by_category': lost_categories,
                'found_by_category': found_categories,
            },
            'recent_activity': {
                'claims': recent_claims,
                'matches': recent_matches,
            }
        })


class AdminUsersListView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUserRole]

    def patch(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        is_active = request.data.get('is_active')
        role = request.data.get('role')

        if is_active is not None:
            if isinstance(is_active, str):
                user.is_active = is_active.lower() in ('true', '1', 'yes')
            else:
                user.is_active = bool(is_active)
        if role and role in dict(User.Role.choices):
            user.role = role

        user.save()

        # Log admin audit
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action_type="UPDATE_USER",
            target_model="User",
            target_id=user.id,
            details=f"Updated User {user.username}: is_active={user.is_active}, role={user.role}",
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({
            'message': 'User updated successfully.',
            'user': UserProfileSerializer(user).data
        })
