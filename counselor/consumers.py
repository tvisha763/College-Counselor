import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import Chat, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authentication check
        if not self.scope["user"].is_authenticated:
            await self.close(code=4003)  # Unauthorized
            return

        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.sender = self.scope['user']

        try:
            self.receiver = await self.get_user(self.receiver_id)
            if self.receiver == self.sender:
                await self.close(code=4002)  # Self-chat not allowed
                return
        except ObjectDoesNotExist:
            await self.close(code=4001)  # Invalid user
            return

        # Create consistent room name
        user_ids = sorted([self.sender.id, int(self.receiver_id)])
        self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Send unread count on connect
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'read_receipt':
                await self.mark_messages_read()
                return
                
            message = data.get('message', '').strip()
            if not message:
                raise ValueError("Message cannot be empty")

            # Save and broadcast message
            timestamp = await self.save_message(message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': str(self.sender.id),
                    'timestamp': timestamp.isoformat(),
                    'is_read': False  # New messages are unread by default
                }
            )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid message format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def chat_message(self, event):
        """Handle incoming chat message"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read']
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def save_message(self, message):
        """Save message and return timestamp"""
        chat = Chat.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message=message
        )
        return chat.timestamp

    @database_sync_to_async
    def mark_messages_read(self):
        """Mark all unread messages as read"""
        Chat.objects.filter(
            receiver=self.sender,
            sender=self.receiver,
            is_read=False
        ).update(is_read=True)

    @database_sync_to_async
    def get_unread_count(self):
        """Get count of unread messages"""
        return Chat.objects.filter(
            receiver=self.sender,
            sender=self.receiver,
            is_read=False
        ).count()
