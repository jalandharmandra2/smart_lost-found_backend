from rest_framework import serializers
from .models import ItemImage

class ItemImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ItemImage
        fields = ('id', 'image', 'image_url', 'is_primary', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
