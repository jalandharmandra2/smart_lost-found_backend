from rest_framework import serializers
from .models import MatchRecord
from lost_items.serializers import LostItemSerializer
from found_items.serializers import FoundItemSerializer

class MatchRecordSerializer(serializers.ModelSerializer):
    lost_item = LostItemSerializer(read_only=True)
    found_item = FoundItemSerializer(read_only=True)
    score_percentage = serializers.SerializerMethodField()

    class Meta:
        model = MatchRecord
        fields = (
            'id', 'lost_item', 'found_item', 'image_similarity', 'category_similarity',
            'color_similarity', 'text_similarity', 'distance_km', 'location_proximity_score',
            'total_score', 'score_percentage', 'match_label', 'status', 'response_notes',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_score_percentage(self, obj):
        return int(round(obj.total_score * 100))


class MatchResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['VIEWED', 'CLAIM_INITIATED', 'CONFIRMED', 'DISMISSED'])
    notes = serializers.CharField(required=False, allow_blank=True)
