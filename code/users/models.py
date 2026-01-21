# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    def create(self, *args, **kwargs):
        raise NotImplementedError("Use create_user() instead of create().")

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not password:
            raise ValueError("Superusers must have a password.")

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True
    )
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)

    def __str__(self):
        return self.username


from django.db import models
from django.conf import settings


class Game(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False,null=False)

    def __str__(self):
        return self.name


class GamerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    favorite_game = models.CharField(max_length=100, blank=True)
    platform = models.CharField(
        max_length=20,
        choices=[
            ("PC", "PC"),
            ("PS5", "PlayStation 5"),
            ("Xbox", "Xbox"),
        ],
        blank=True,
    )
    ign = models.CharField(max_length=100, blank=True)  # in-game name
    bio = models.TextField(blank=True)

    games = models.ManyToManyField(Game, related_name="players", blank=True)
    allow_game_search = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
    )
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")

    def accept(self):
        self.is_accepted = True
        self.save()
        self.from_user.friends.add(self.to_user)
        self.to_user.friends.add(self.from_user)

    def decline(self):
        self.delete()

    def __str__(self):
        return f"{self.from_user} ➡️ {self.to_user} ({'Accepted' if self.is_accepted else 'Pending'})"
