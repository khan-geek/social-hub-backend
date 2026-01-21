from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Read the access token from the 'access' cookie
        raw_token = request.COOKIES.get("access")
        print("authentication token", raw_token)
        if raw_token is None:
            return None  # No token = unauthenticated

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception:
            return None  # Invalid token = unauthenticated
