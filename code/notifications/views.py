from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(ReadOnlyModelViewSet):
    """
    Read-only ViewSet for listing and marking notifications as read.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Only return notifications for the logged-in user.
        Optional filter: ?is_read=false
        """
        queryset = Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        return queryset

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """
        Custom action to mark all unread notifications as read.
        """
        count = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({"message": f"{count} notifications marked as read."})
