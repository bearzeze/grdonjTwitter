# Log-in via email and password also

from django.contrib.auth import get_user_model

def authenticate_via_email(request, email=None, password=None, **kwargs):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(email=email)
        if user.check_password(password):
            return user
        else:
            raise PasswordIncorrectExecption
        
    except (UserModel.DoesNotExist, PasswordIncorrectExecption):
        return None


class PasswordIncorrectExecption(Exception):
    pass