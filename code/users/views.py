from rest_framework import generics
from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        print(serializer.validated_data)
        
        serializer.save()

    # def create(self, request, *args, **kwargs):
    #     print("hello world")
    #     serializer = self.get_serializer(data=request.data)

    #     if serializer.is_valid():
    #         print("valid")
    #         # Optionally save: serializer.save()
    #         return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     else:
    #         print("not valid")
    #         return Response(
    #             {"error": "An error occurred", "details": serializer.errors},
    #             status=status.HTTP_403_FORBIDDEN
    #         )

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from notifications.models import Notification
from rest_framework.permissions import IsAdminUser



class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        if(request.user.is_staff):
            super().list(request,*args, **kwargs)
        else:
            return Response({'error' : 'Not Authorized'})
    @action(detail=True, methods=["post"])
    def follow(self, request, pk=None):
        user_to_follow = self.get_object()

        if user_to_follow == request.user:
            return Response({"error": "You cannot follow yourself."}, status=400)

        if user_to_follow in request.user.following.all():
            return Response({"message": "You are already following this user."})

        request.user.following.add(user_to_follow)

        # Optional: send notification
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            notif_type="follow"
        )

        return Response({"message": f"You are now following {user_to_follow.username}"})

    @action(detail=True, methods=["post"])
    def unfollow(self, request, pk=None):
        user_to_unfollow = self.get_object()

        if user_to_unfollow not in request.user.following.all():
            return Response({"message": "You are not following this user."}, status=400)

        request.user.following.remove(user_to_unfollow)

        return Response({"message": f"You have unfollowed {user_to_unfollow.username}"})

from .serializers import GamerProfile

class UserSearchByGameView(generics.ListAPIView):
    serializer_class = GamerProfile  # or GamerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        game_name = self.request.query_params.get('game')
        if game_name:
            return User.objects.filter(
                gamerprofile__games__name__icontains=game_name,
                gamerprofile__allow_game_search=True
            ).distinct()
        return User.objects.none()

from rest_framework.viewsets import ModelViewSet
from .models import GamerProfile
from .serializers import GamerProfileWriteSerializer

class GamerProfileViewSet(ModelViewSet):
    serializer_class = GamerProfileWriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GamerProfile.objects.filter(user=self.request.user)


    def get_object(self):
        try:
            return self.request.user.gamerprofile
        except GamerProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("You have not created a gamer profile yet.")

    def perform_update(self, serializer):
        serializer.save()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

from .models import FriendRequest
from .serializers import FriendRequestSerializer

class FriendRequestViewSet(ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user) | FriendRequest.objects.filter(from_user=user)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        fr = self.get_object()
        if fr.to_user != request.user:
            return Response({'detail': 'Not authorized'}, status=403)
        fr.accept()
        return Response({'detail': 'Friend request accepted'})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        fr = self.get_object()
        if fr.to_user != request.user:
            return Response({'detail': 'Not authorized'}, status=403)
        fr.decline()
        return Response({'detail': 'Friend request declined'})

from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.timezone import now
from .serializers import CustomTokenObtainPairSerializer
import datetime

# Custom Login View - returns HttpOnly cookies
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            data = response.data
            access = data.get("access")
            refresh = data.get("refresh")

            expires = now() + datetime.timedelta(days=7)

            response.set_cookie(
                key='access',
                value=access,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=300  # 5 minutes
            )
            response.set_cookie(
                key='refresh',
                value=refresh,
                httponly=True,
                secure=False,
                samesite='Lax',
                expires=expires
            )

            # Optional: remove from JSON body
            del response.data['access']
            del response.data['refresh']
        print(response.cookies)
        return response
# Refresh Token View (reads refresh token from cookie)
class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        print("refresh token", refresh_token)
        print("cookies", request.COOKIES)
        if not refresh_token:
            return Response({"detail": "Refresh token not found."}, status=401)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            response = Response(status=200)
            response.set_cookie(
                key='access',
                value=access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=300
            )

            return response
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=401)

# Logout View - blacklist refresh token and clear cookies
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # optional: log error

        response = Response({"message": "Logged out successfully."}, status=200)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response
