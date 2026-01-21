# Create your views here.
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "bio", "avatar"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
            bio=validated_data.get("bio", ""),
            avatar=validated_data.get("avatar", None),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    is_friend = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "bio",
            "avatar",
            "followers",
            "following",
            "is_friend",
            "is_following",
            "first_name",
            "last_name",
        ]

    def get_is_friend(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return obj in user.friends.all()

    def get_is_following(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return obj in user.following.all()

    @staticmethod
    def hello():
        print("hello")
from .models import GamerProfile, Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["id", "name"]


class GamerProfileSerializer(serializers.ModelSerializer):
    games = GameSerializer(many=True, read_only=True)
    # games = serializers.SlugRelatedField(
    #     many=True, slug_field="name", queryset=Game.objects.all()
    # )

    class Meta:
        model = GamerProfile
        fields = [
            "favorite_game",
            "platform",
            "ign",
            "bio",
            "games",
            "allow_game_search",
        ]


class GamerProfileWriteSerializer(serializers.ModelSerializer):
    games = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), many=True)

    class Meta:
        model = GamerProfile
        fields = [
            "favorite_game",
            "platform",
            "ign",
            "bio",
            "games",
            "allow_game_search",
        ]


from .models import FriendRequest


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ["id", "from_user", "to_user", "is_accepted", "created_at"]
        read_only_fields = ["from_user", "is_accepted", "created_at"]


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD  # typically 'username'

    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        # Try to find user by username or email
        user = (
            User.objects.filter(username__iexact=username_or_email).first()
            or User.objects.filter(email__iexact=username_or_email).first()
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        # Attach validated user to self
        self.user = user
        return super().validate(attrs)

#class CustomToken:
