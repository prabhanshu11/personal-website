"""Gmail API client — fetches transactional emails using OAuth2.

Token is stored as JSON (portable across Docker containers).
Supports incremental sync via Gmail History API.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .config import get_settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Query for transactional emails from Indian banks and services
TRANSACTION_QUERY = (
    "from:(alerts@hdfcbank.net OR noreply@hdfcbank.com OR "
    "alerts@iob.in OR noreply@iob.in OR "
    "noreply@swiggy.in OR noreply@blinkit.com OR "
    "alerts@hdfcbank.net) "
    "subject:(transaction OR debited OR credited OR order OR payment OR statement)"
)


class GmailClient:
    """Async-friendly Gmail API client with JSON token storage."""

    def __init__(self):
        settings = get_settings()
        self.credentials_path = Path(settings.gmail_credentials_path)
        self.token_path = Path(settings.gmail_token_path)
        self._service = None

    def _load_credentials(self) -> Optional[Credentials]:
        """Load saved credentials from JSON token file."""
        if not self.token_path.exists():
            return None
        with open(self.token_path, "r") as f:
            token_data = json.load(f)
        return Credentials.from_authorized_user_info(token_data, SCOPES)

    def _save_credentials(self, creds: Credentials) -> None:
        """Save credentials to JSON token file."""
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_path, "w") as f:
            f.write(creds.to_json())

    def authenticate(self) -> Credentials:
        """Authenticate with Gmail API. Returns valid credentials.

        First run requires browser-based OAuth flow (run locally).
        Subsequent runs use the saved token with auto-refresh.
        """
        creds = self._load_credentials()

        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired Gmail credentials...")
            creds.refresh(Request())
            self._save_credentials(creds)
            return creds

        # Fresh OAuth flow — requires browser (local setup only)
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Gmail credentials not found at {self.credentials_path}. "
                "Download from Google Cloud Console → APIs & Services → Credentials."
            )

        logger.info("Starting OAuth flow — this requires a browser...")
        flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
        creds = flow.run_local_server(port=0)
        self._save_credentials(creds)
        return creds

    @property
    def service(self):
        """Lazily build the Gmail API service."""
        if self._service is None:
            creds = self.authenticate()
            self._service = build("gmail", "v1", credentials=creds)
        return self._service

    async def fetch_messages(
        self, query: str = TRANSACTION_QUERY, max_results: int = 50
    ) -> list[dict]:
        """Fetch messages matching query. Returns list of message dicts."""
        def _fetch():
            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
            return results.get("messages", [])

        return await asyncio.to_thread(_fetch)

    async def get_message(self, msg_id: str) -> dict:
        """Get full message details by ID."""
        def _get():
            return (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )

        return await asyncio.to_thread(_get)

    async def fetch_messages_since_history(
        self, history_id: str, max_results: int = 100
    ) -> tuple[list[dict], Optional[str]]:
        """Incremental sync: fetch messages added since a history ID.

        Returns (message_list, new_history_id).
        Falls back to full query if history is expired.
        """
        def _history():
            try:
                results = (
                    self.service.users()
                    .history()
                    .list(
                        userId="me",
                        startHistoryId=history_id,
                        historyTypes=["messageAdded"],
                        maxResults=max_results,
                    )
                    .execute()
                )
                new_history_id = results.get("historyId")
                messages = []
                for record in results.get("history", []):
                    for msg_added in record.get("messagesAdded", []):
                        messages.append(msg_added["message"])
                return messages, new_history_id
            except Exception as e:
                if "404" in str(e) or "historyId" in str(e).lower():
                    logger.warning("History ID expired, falling back to full query")
                    return None, None
                raise

        messages, new_history_id = await asyncio.to_thread(_history)
        if messages is None:
            # Fallback to full query
            messages = await self.fetch_messages()
            return messages, None
        return messages, new_history_id

    async def get_current_history_id(self) -> str:
        """Get the current history ID for the mailbox."""
        def _profile():
            return self.service.users().getProfile(userId="me").execute()

        profile = await asyncio.to_thread(_profile)
        return profile["historyId"]

    @staticmethod
    def extract_headers(message: dict) -> dict[str, str]:
        """Extract common headers from a Gmail message."""
        headers = message.get("payload", {}).get("headers", [])
        result = {}
        for h in headers:
            name = h["name"].lower()
            if name in ("from", "to", "subject", "date"):
                result[name] = h["value"]
        return result

    @staticmethod
    def extract_body_text(message: dict) -> str:
        """Extract plain text body from a Gmail message."""
        payload = message.get("payload", {})

        # Simple single-part message
        if "body" in payload and payload["body"].get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

        # Multipart message — find text/plain
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode(
                    "utf-8", errors="replace"
                )

        # Fallback to snippet
        return message.get("snippet", "")
