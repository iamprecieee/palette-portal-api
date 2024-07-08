from django.conf import settings
from django.contrib.sessions.exceptions import SessionInterrupted

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class SessionRefreshToken:
    def __init__(self, request):
        self.session = request.session

        """
        For storing refresh tokens directly in session,
        and not having to manually input it in request data.
        """
        refresh = self.session.get(settings.REFRESH_SESSION_ID)
        if not refresh:
            refresh = self.session[settings.REFRESH_SESSION_ID] = {}

        self.refresh = refresh

    def save(self):
        self.session.modified = True

    def add(self, refresh_token):
        self.refresh["refresh"] = refresh_token
        self.save()

    def token(self):
        return self.refresh["refresh"]

    # Method for blacklisting refresh token to be removed from session
    def remove(self, modify=False):
        if self.session["refresh"]:
            refresh_token = self.token()
            try:
                refresh = RefreshToken(refresh_token)
                if settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]:
                    if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]:
                        try:
                            refresh.blacklist()
                        except AttributeError:
                            pass

                    refresh.set_jti()
                    refresh.set_exp()
                    refresh.set_iat()

                del self.refresh["refresh"]
                self.save()
            except (TokenError, SessionInterrupted):
                # Deletes session data and regenerates a new session key
                self.session.flush()
