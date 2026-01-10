from rest_framework import serializers
from .models import Category


class RecursiveCategorySerializer(serializers.Serializer):
    """
    Used internally to recursively serialize sub-categories
    """

    def to_representation(self, instance):
        return CategorySerializer(instance, context=self.context).data


class CategorySerializer(serializers.ModelSerializer):
    """
    Main serializer for Category
    """

    sub_categories = serializers.SerializerMethodField()

    parent_category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "image_url",
            "parent_category",
            "parent_category_id",
            "active",
            "sub_categories",
        ]
        read_only_fields = ["parent_category"]

    def get_sub_categories(self, obj):
        """
        Return only non-deleted child categories
        """
        children_qs = obj.children.filter(delete_status=0)
        return RecursiveCategorySerializer(children_qs, many=True, context=self.context).data

    def validate_parent_category_id(self, value):
        """
        Validate parent category existence and deletion status
        """
        if value is None:
            return value

        if not Category.objects.filter(id=value, delete_status=0).exists():
            raise serializers.ValidationError("Invalid or deleted parent category")
        return value

    def create(self, validated_data):
        """
        Handle parent_category assignment using parent_category_id
        """
        parent_id = validated_data.pop("parent_category_id", None)

        if parent_id:
            validated_data["parent_category"] = Category.objects.get(id=parent_id, delete_status=0)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Allow updating parent category safely (PATCH support)
        """
        parent_id = validated_data.pop("parent_category_id", None)

        if parent_id is not None:
            instance.parent_category = (
                Category.objects.get(id=parent_id, delete_status=0) if parent_id else None
            )

        return super().update(instance, validated_data)
