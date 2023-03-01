from django.urls import path

from .views import HomeView, SlackAuthCallbackView, SlackWebhookView, UserView

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home-view"),
    path(
        "slack-auth-callback/",
        SlackAuthCallbackView.as_view(),
        name="slack-auth-callback",
    ),
    path("slack-webhook/", SlackWebhookView.as_view(), name="slack-webhook"),
    path("user/", UserView.as_view(), name="user-view"),
]
