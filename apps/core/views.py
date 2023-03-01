import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.slack_webhook_url:
            client_id = settings.SLACK_CLIENT_ID
            scopes = settings.SLACK_SCOPES
            user_scopes = settings.SLACK_USER_SCOPES
            base_url = settings.SLACK_AUTH_URL
            context[
                "slack_auth_url"
            ] = f"{base_url}?client_id={client_id}&scope={scopes}&user_scope={user_scopes}"

        return context


class SlackAuthCallbackView(APIView):
    """
    Slack auth callback view to get slack webhook url.
    This View is called by slack after user authorizes the app
    """

    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        user = request.user
        logger.warning("slack auth callback view executed")
        logger.warning("the request user is")
        logger.warning(user)
        # send request to slack to get access token
        url = "https://slack.com/api/oauth.v2.access"
        data = {
            "client_id": settings.SLACK_CLIENT_ID,
            "client_secret": settings.SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.BASE_URL + reverse("core:slack-auth-callback"),
        }
        response = requests.post(url, data=data)
        response_data = response.json()
        logger.warning(f"the response data is {response_data}")
        # extract webhook url from response
        webhook_dict = response_data.get("incoming_webhook", {})
        webhook_url = webhook_dict.get("url")
        logger.warning("the webhook url is")
        logger.warning(webhook_url)
        # save webhook url in db
        user.slack_webhook_url = webhook_url
        user.save()
        logger.warning("slack webhook url saved in db")
        messages.add_message(
            request, messages.SUCCESS, "Connected to Slack successfully.!"
        )
        return redirect(reverse("core:workflow"))
