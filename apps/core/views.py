import json
import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)
User = get_user_model()


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if self.request.user.slack_webhook_url:
                context["slack_auth_url"] = None
            else:
                client_id = settings.SLACK_CLIENT_ID
                scopes = settings.SLACK_SCOPES
                user_scopes = settings.SLACK_USER_SCOPES
                base_url = settings.SLACK_AUTH_URL
                context[
                    "slack_auth_url"
                ] = f"{base_url}?client_id={client_id}&scope={scopes}&user_scope={user_scopes}"
        return context


class SlackWebhookView(APIView):
    """
    Slack webhook view to send message to slack workspace.
    note - it will only send messages to users who have connected their slack account
    """

    def post(self, request, *args, **kwargs):
        all_slack_users = User.objects.filter(slack_webhook_url__isnull=False)
        request_type = request.data.get("Type")
        if request_type == "SpamNotification":
            email = request.data.get("Email")
            for user in all_slack_users:
                slack_webhook_url = user.slack_webhook_url
                slack_data = {
                    "text": f"Hello {user.username},",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"There is a spam notification from {email}",
                            },
                        }
                    ],
                }
                logger.warning("sending below data to slack")
                logger.warning(slack_data)
                response = requests.post(
                    slack_webhook_url,
                    data=json.dumps(slack_data),
                    headers={"Content-Type": "application/json"},
                )
                logger.warning(f"slack response {response.text}")

        return Response({"msg": True}, status=200)


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
