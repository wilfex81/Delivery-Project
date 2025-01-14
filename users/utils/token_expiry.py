from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from datetime import datetime, timedelta

class ExpiringPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
    
    def make_token(self, user):
        timestamp = int((datetime.now() + timedelta(hours=1)).timestamp())
        return super().make_token(user) + str(timestamp)

    def check_token(self, user, token):
        try:
            ts_str = token[-10:]
            token = token[:-10]
            timestamp = int(ts_str)
        except ValueError:
            return False

        if datetime.fromtimestamp(timestamp) < datetime.now():
            return False

        return super().check_token(user, token)    
