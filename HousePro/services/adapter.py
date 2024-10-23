from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def get_app(self, request, provider):
        try:
            # Filter based on the provider and only return the specific one
            return SocialApp.objects.get(provider=provider, sites__id=settings.SITE_ID)
        except MultipleObjectsReturned:
            # In case of duplicates, force selection of the correct app by ID or name
            return SocialApp.objects.filter(provider=provider, sites__id=settings.SITE_ID).first()