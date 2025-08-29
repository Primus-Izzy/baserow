from rest_framework import serializers
from baserow.contrib.dashboard.models import Dashboard, DashboardPermission, DashboardExport


class PublicLinkSerializer(serializers.Serializer):
    """Serializer for creating public dashboard links."""
    
    def to_representation(self, instance):
        return {
            'public_url': instance['public_url'],
            'token': instance['token']
        }


class EmbedLinkSerializer(serializers.Serializer):
    """Serializer for creating embed links."""
    widget_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="List of widget IDs to embed. If not provided, entire dashboard will be embeddable."
    )
    
    def to_representation(self, instance):
        if 'widgets' in instance:
            return {
                'widgets': instance['widgets']
            }
        else:
            return {
                'embed_url': instance['embed_url'],
                'token': instance['token']
            }


class DashboardPermissionSerializer(serializers.ModelSerializer):
    """Serializer for dashboard permissions."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    granted_by_email = serializers.EmailField(source='granted_by.email', read_only=True)
    
    class Meta:
        model = DashboardPermission
        fields = [
            'user_email', 'permission_type', 'granted_by_email', 'created_at'
        ]
        read_only_fields = ['granted_by_email', 'created_at']


class SetPermissionSerializer(serializers.Serializer):
    """Serializer for setting dashboard permissions."""
    
    user_email = serializers.EmailField()
    permission_type = serializers.ChoiceField(choices=DashboardPermission.PERMISSION_TYPES)
    
    def validate_user_email(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(email=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")


class RemovePermissionSerializer(serializers.Serializer):
    """Serializer for removing dashboard permissions."""
    
    user_email = serializers.EmailField()
    
    def validate_user_email(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(email=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")


class DashboardSharingSettingsSerializer(serializers.ModelSerializer):
    """Serializer for dashboard sharing settings."""
    
    public_url = serializers.SerializerMethodField()
    embed_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'permission_level', 'public_token', 'embed_token',
            'public_url', 'embed_url'
        ]
        read_only_fields = ['public_token', 'embed_token', 'public_url', 'embed_url']
    
    def get_public_url(self, obj):
        if obj.public_token and obj.permission_level == 'public':
            from django.conf import settings
            return f"{settings.PUBLIC_BACKEND_URL}/dashboard/public/{obj.public_token}"
        return None
    
    def get_embed_url(self, obj):
        if obj.embed_token:
            from django.conf import settings
            return f"{settings.PUBLIC_BACKEND_URL}/dashboard/embed/{obj.embed_token}"
        return None