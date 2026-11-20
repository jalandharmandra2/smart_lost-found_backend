from rest_framework import serializers
from .models import ClaimRequest
from accounts.serializers import PublicUserSerializer
from found_items.serializers import FoundItemSerializer
from lost_items.serializers import LostItemSerializer
from notifications.services import notify_claim_submitted, notify_claim_status_updated

class ClaimRequestSerializer(serializers.ModelSerializer):
    claimant = PublicUserSerializer(read_only=True)
    found_item_details = FoundItemSerializer(source='found_item', read_only=True)
    lost_item_details = LostItemSerializer(source='lost_item', read_only=True)

    class Meta:
        model = ClaimRequest
        fields = (
            'id', 'claimant', 'found_item', 'found_item_details', 'lost_item',
            'lost_item_details', 'claim_description', 'secret_identifying_answers',
            'supporting_document', 'status', 'finder_response', 'admin_notes',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'status', 'finder_response', 'admin_notes', 'created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None

        is_claimant = user and user.is_authenticated and instance.claimant_id == user.id
        is_finder = user and user.is_authenticated and instance.found_item.user_id == user.id
        is_admin = user and user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'ADMINISTRATOR')

        # Redact private verification proofs if not claimant, finder, or administrator
        if not (is_claimant or is_finder or is_admin):
            data['secret_identifying_answers'] = "[REDACTED - Visible only to involved parties and administrators]"

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['claimant'] = request.user
        claim = ClaimRequest.objects.create(**validated_data)
        
        # Trigger notifications
        try:
            notify_claim_submitted(claim)
        except Exception:
            pass

        return claim


class ClaimStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ClaimRequest.STATUS_CHOICES)
    response_notes = serializers.CharField(required=False, allow_blank=True)
