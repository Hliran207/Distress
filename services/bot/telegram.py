import requests

from distress_core.settings import TelegramSettings

API_URL = "https://api.telegram.org/bot{token}/{method}"


class TelegramError(Exception):
    """A failed call to the Telegram API. Never contains the bot token."""


class TelegramClient:
    """Minimal client for the Telegram Bot API: long polling with getUpdates."""

    def __init__(self, settings: TelegramSettings) -> None:
        self._token = settings.telegram_bot_token.get_secret_value()
        self._poll_timeout = settings.telegram_poll_timeout
        self._session = requests.Session()

    def get_updates(self, offset: int | None) -> list[dict]:
        """Wait for updates newer than `offset`.

        Passing an offset acknowledges every update before it: Telegram will not resend them.
        """
        params = {"timeout": self._poll_timeout, "allowed_updates": '["message"]'}
        if offset is not None:
            params["offset"] = offset

        try:
            response = self._session.get(
                API_URL.format(token=self._token, method="getUpdates"),
                params=params,
                timeout=self._poll_timeout + 10,
            )
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise TelegramError(
                f"{type(exc).__name__} (HTTP call to Telegram failed)"
            ) from None
            # from none because we want to raise the exception without the url token.

        if not body.get("ok"):
            raise TelegramError(
                f"Telegram error {body.get('error_code')}: {body.get('description')}"
            )
        return body["result"]
