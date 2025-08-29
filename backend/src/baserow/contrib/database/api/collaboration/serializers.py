from rest_framework import serializers

from baserow.contrib.database.collaboration.models import (
    ActivityLog,
    Comment,
    UserPresence,
)


class UserPresenceSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.first_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserPresence
        fields = [
            "user",
            "user_name", 
            "user_email",
            "last_seen",
            "cursor_position",
            "is_typing",
            "typing_field_id",
            "typing_row_id",
        ]
        read_only_fields = ["user", "user_name", "user_email", "last_seen"]


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.first_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    replies = serializers.SerializerMethodField()
    mentions = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "user",
            "user_name",
            "user_email", 
            "parent",
            "created_at",
            "updated_at",
            "is_resolved",
            "replies",
            "mentions",
        ]
        read_only_fields = ["user", "user_name", "user_email", "created_at", "updated_at"]

    def get_replies(self, obj):
        if obj.parent is None:
            replies = Comment.objects.filter(parent=obj).select_related("user").prefetch_related("mentions")
            return CommentSerializer(replies, many=True, context=self.context).data
        return []

    def get_mentions(self, obj):
        return [
            {
                "id": user.id,
                "first_name": user.first_name,
                "email": user.email,
            }
            for user in obj.mentions.all()
        ]


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "parent"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["table"] = self.context["table"]
        validated_data["row_id"] = self.context["row_id"]
        return super().create(validated_data)


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.first_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "action_type",
            "details",
            "timestamp",
        ]
        read_only_fields = ["user", "user_name", "user_email", "timestamp"]


class CollaborationStatsSerializer(serializers.Serializer):
    active_users = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    recent_comments = serializers.IntegerField()