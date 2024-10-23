from django.contrib.auth import get_user_model

def set_user_type(strategy, details, user=None, *args, **kwargs):
    """
    Sets the user type after logging in through Google.
    """
    if user and not user.is_master:
        user.is_master = False
        user.save()

def associate_by_email(backend, details, user=None, *args, **kwargs):
    """
    If a user already exists with the same email, link the Google account
    with the existing user.
    """
    if user:
        return None

    User = get_user_model()
    email = details.get('email')

    if email:
        try:
            # Try to find user with such email
            user = User.objects.get(email=email)
            return {'user': user}
        except User.DoesNotExist:
            return None