from rest_framework import serializers
from .models import Tag, StockMovement

class ScanSerializer(serializers.Serializer):
    uid = serializers.CharField()
    direction = serializers.ChoiceField(choices=['IN', 'OUT'])
    location = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        uid = validated_data['uid']
        direction = validated_data['direction']
        location = validated_data.get('location', '')

        try:
            tag = Tag.objects.select_related('item').get(uid=uid)
        except Tag.DoesNotExist:
            raise serializers.ValidationError({"uid": "Unknown tag UID"})

        movement = StockMovement.objects.create(
            item=tag.item,
            direction=direction,
            location=location,
            quantity=1,
        )
        return movement
