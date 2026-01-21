import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

""" class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = self.scope['user'].id

        saved_message = await self.save_message(self.room_id, sender_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_message.content,
                "sender": saved_message.sender.username,
                "timestamp": str(saved_message.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
        }))

    @database_sync_to_async
    def save_message(self, room_id, sender_id, message):
        return Message.objects.create(
            room_id=room_id,
            sender_id=sender_id,
            content=message
        )
 """



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'message':
            message = data['message']
            sender = self.scope['user']

            msg_obj = await self.save_message(sender, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.username,
                    'timestamp': msg_obj.timestamp.isoformat(),
                }
            )

        elif message_type == 'seen':
            await self.mark_messages_as_read()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def save_message(self, sender, message):
        room = ChatRoom.objects.get(id=self.room_id)
        msg = Message.objects.create(room=room, sender=sender, content=message)
        msg.read_by.add(sender)  # Sender has read their own message
        return msg

    @database_sync_to_async
    def mark_messages_as_read(self):
        user = self.scope['user']
        room = ChatRoom.objects.get(id=self.room_id)
        unread_messages = Message.objects.filter(room=room).exclude(read_by=user)
        for msg in unread_messages:
            msg.read_by.add(user)
