from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.db.models import Count
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoomViewSet(ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

    @action(detail=False, methods=["post"])
    def get_or_create_dm(self, request):
        """
        Ensure only one DM room exists between two users.
        """
        user_id = request.data.get("user_id")
        user2 = request.user

        try:
            user1 = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user1 == user2:
            return Response({"error": "Can't chat with yourself."}, status=400)

        # Check if there's already a room between both
        rooms = (
            ChatRoom.objects.annotate(num_participants=Count("participants"))
            .filter(participants=user1)
            .filter(participants=user2)
            .filter(is_group=False)
            .filter(num_participants=2)
        )

        if rooms.exists():
            room = rooms.first()
        else:
            room = ChatRoom.objects.create(is_group=False)
            room.participants.set([user1, user2])

        serializer = self.get_serializer(room)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        room = self.get_object()
        user = request.user
        messages = room.messages.exclude(read_by=user)
        for msg in messages:
            msg.read_by.add(user)
        return Response({"message": "All messages marked as read."})

    def get_unread_count(self, user, room):
        return room.messages.exclude(read_by=user).count()

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        room = self.get_object()
        messages = room.messages.order_by("timestamp")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(room__participants=self.request.user)

    def perform_create(self, serializer):
        room = serializer.validated_data["room"]
        if self.request.user not in room.participants.all():
            raise PermissionError("You are not a participant in this chat.")
        serializer.save(sender=self.request.user)
