from rest_framework import serializers
from .models import LostItem
from accounts.serializers import PublicUserSerializer
from item_images.serializers import ItemImageSerializer
from item_images.models import ItemImage
from ai_matching.services import extract_clip_embedding

class LostItemSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    images = ItemImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    # Single image convenience field for quick form uploads
    image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = LostItem
        fields = (
            'id', 'user', 'item_name', 'category', 'description', 'colour',
            'brand_or_maker', 'date_lost', 'location', 'latitude', 'longitude',
            'contact_preference', 'secret_identifying_details', 'reward_amount',
            'status', 'is_active', 'images', 'uploaded_images', 'image',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'is_active', 'created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None

        # Redact confidential identifying details unless user is the owner or an admin
        is_owner = user and user.is_authenticated and instance.user_id == user.id
        is_admin = user and user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'ADMINISTRATOR')

        if not (is_owner or is_admin):
            data['secret_identifying_details'] = "[REDACTED - Visible only to verified owner and administrators]"

        return data

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        single_image = validated_data.pop('image', None)
        if single_image:
            uploaded_images.append(single_image)

        request = self.context.get('request')
        user = request.user if request else None
        lost_item = LostItem.objects.create(user=user, **validated_data)

        # Process uploaded images and compute embeddings
        is_first = True
        for img_file in uploaded_images:
            item_img = ItemImage.objects.create(
                lost_item=lost_item,
                image=img_file,
                is_primary=is_first
            )
            is_first = False
            try:
                embedding = extract_clip_embedding(item_img.image.path)
                if embedding:
                    item_img.embedding = embedding
                    item_img.save(update_fields=['embedding'])
            except Exception as e:
                pass

        return lost_item

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
                    lost_item=instance,
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
