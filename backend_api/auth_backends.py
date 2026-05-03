import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class EmailMultiTenantBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
            
        try:
            users = UserModel.objects.filter(**{UserModel.USERNAME_FIELD: username})
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
        except Exception as e:
            logger.error(f"MultiTenant Auth Error: {e}")
            return None
        return None
