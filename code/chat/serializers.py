from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    read_by = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "room",
            "sender",
            "sender_username",
            "content",
            "timestamp",
            "read_by",
        ]
        read_only_fields = ["sender", "timestamp", "sender_username", "read_by"]


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True
    )
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "participants",
            "is_group",
            "created_at",
            "unread_count",
        ]
        read_only_fields = ["created_at"]

    def get_unread_count(self, obj):
        user = self.context["request"].user
        return obj.messages.exclude(read_by=user).count()
