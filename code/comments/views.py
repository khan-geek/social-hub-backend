from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Comment
from .serializers import CommentSerializer
from core.permissions import IsAuthorOrReadOnly

class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        if comment.post.author != self.request.user:
            from notifications.models import Notification  # avoid circular import

            Notification.objects.create(
                recipient=comment.post.author,
                sender=self.request.user,
                notif_type="comment",
                post=comment.post,
            )
    def get_queryset(self):
        queryset = Comment.objects.all().order_by("-created_at")
        post_id = self.request.query_params.get("post")

        if post_id:
            queryset = queryset.filter(post_id=post_id)

        return queryset
