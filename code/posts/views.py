from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import IsAuthorOrReadOnly
from .models import Post
from .serializers import PostSerializer
from notifications.models import Notification

class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if post.liked_by.filter(id=user.id).exists():
            return Response({"message": "You already liked this post."}, status=400)

        post.liked_by.add(user)

        if post.author != user:
            Notification.objects.create(
                recipient=post.author,
                sender=user,
                notif_type='like',
                post=post
            )

        return Response({"message": "Post liked."})

    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if not post.liked_by.filter(id=user.id).exists():
            return Response({"message": "You haven't liked this post."}, status=400)

        post.liked_by.remove(user)
        return Response({"message": "Post unliked."})
    def get_queryset(self):
        user = self.request.user
        # Show posts from:
        # - Friends
        # - OR people the user follows
        friends = user.friends.all()
        follows = user.following.all()  # assuming a related_name="following"
        from itertools import chain
        return Post.objects.filter(
            author__in=list(chain(friends, follows, [user]))
        ).distinct()
