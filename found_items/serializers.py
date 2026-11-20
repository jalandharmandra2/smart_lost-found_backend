from rest_framework import serializers
from .models import FoundItem
from accounts.serializers import PublicUserSerializer
from item_images.serializers import ItemImageSerializer
from item_images.models import ItemImage
from ai_matching.services import extract_clip_embedding

class FoundItemSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    images = ItemImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = FoundItem
        fields = (
            'id', 'user', 'item_name', 'category', 'description', 'colour',
            'date_found', 'found_location', 'latitude', 'longitude',
            'current_storage_location', 'status', 'is_active', 'images',
            'uploaded_images', 'image', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'is_active', 'created_at', 'updated_at')

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        single_image = validated_data.pop('image', None)
        if single_image:
            uploaded_images.append(single_image)

        request = self.context.get('request')
        user = request.user if request else None
        found_item = FoundItem.objects.create(user=user, **validated_data)

        is_first = True
        for img_file in uploaded_images:
            item_img = ItemImage.objects.create(
                found_item=found_item,
                image=img_file,
                is_primary=is_first
            )
            is_first = False
            try:
                embedding = extract_clip_embedding(item_img.image.path)
                if embedding:
                    item_img.embedding = embedding
                    item_img.save(update_fields=['embedding'])
            except Exception:
                pass

        return found_item

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        single_image = validated_data.pop('image', None)
        if single_image:
            uploaded_images.append(single_image)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if uploaded_images:
            for img_file in uploaded_images:
                item_img = ItemImage.objects.create(
                    found_item=instance,
                    image=img_file,
                    is_primary=(instance.images.count() == 0)
                )
                try:
                    embedding = extract_clip_embedding(item_img.image.path)
                    if embedding:
                        item_img.embedding = embedding
                        item_img.save(update_fields=['embedding'])
                except Exception:
                    pass

        return instance
