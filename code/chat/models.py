from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, blank=True)  # For group names
    participants = models.ManyToManyField(User, related_name='chatrooms')
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_group:
            return self.name or f"Group Chat {self.id}"
        else:
            usernames = [u.username for u in self.participants.all()]
            return f"{usernames[0]} ↔ {usernames[1]}" if len(usernames) == 2 else f"ChatRoom {self.id}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)  
    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
