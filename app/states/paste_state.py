import reflex as rx
from typing import Literal, TypedDict, Optional
import uuid
from datetime import datetime, timedelta
import logging

Expiration = Literal["1h", "1d", "1w", "never"]


class Paste(TypedDict):
    """A paste with its content and metadata."""

    id: str
    content: str
    language: str
    created_at: datetime
    expires_at: Optional[datetime]


class PasteState(rx.State):
    """Manages the state for creating and viewing pastes."""

    content: str = ""
    language: str = "python"
    expiration: Expiration = "1d"
    pastes: dict[str, Paste] = {}
    current_paste: Optional[Paste] = None
    languages: list[str] = [
        "python",
        "javascript",
        "typescript",
        "java",
        "csharp",
        "html",
        "css",
        "sql",
        "json",
        "markdown",
        "rust",
        "go",
        "bash",
    ]
    expiration_options: list[dict[str, str]] = [
        {"value": "1h", "label": "1 Hour"},
        {"value": "1d", "label": "1 Day"},
        {"value": "1w", "label": "1 Week"},
        {"value": "never", "label": "Never"},
    ]

    @rx.event
    def create_paste(self):
        """Creates a new paste, stores it, and redirects to its page."""
        if not self.content.strip():
            return rx.toast.error("Paste content cannot be empty.")
        paste_id = uuid.uuid4().hex
        now = datetime.utcnow()
        expires_at = None
        if self.expiration == "1h":
            expires_at = now + timedelta(hours=1)
        elif self.expiration == "1d":
            expires_at = now + timedelta(days=1)
        elif self.expiration == "1w":
            expires_at = now + timedelta(weeks=1)
        new_paste: Paste = {
            "id": paste_id,
            "content": self.content,
            "language": self.language,
            "created_at": now,
            "expires_at": expires_at,
        }
        self.pastes[paste_id] = new_paste
        self.content = ""
        yield rx.toast.success("Paste created successfully!")
        return rx.redirect(f"/paste/{paste_id}")

    @rx.event
    def load_paste(self):
        """Loads a paste by its ID from the URL parameter."""
        try:
            paste_id = self.router.page.params.get("paste_id", "")
        except Exception as e:
            logging.exception(f"Error getting paste_id: {e}")
            paste_id = ""
        if not paste_id:
            self.current_paste = None
            return rx.toast.error("Invalid paste ID.")
        paste = self.pastes.get(paste_id)
        if not paste:
            self.current_paste = None
            return rx.toast.error("Paste not found.")
        if paste["expires_at"] and datetime.utcnow() > paste["expires_at"]:
            del self.pastes[paste_id]
            self.current_paste = None
            return rx.toast.warning("This paste has expired.")
        self.current_paste = paste

    @rx.event
    def clear_content(self):
        """Clears the textarea content."""
        self.content = ""

    @rx.event
    def show_settings(self):
        """Placeholder for showing settings."""
        return rx.toast.info("Settings clicked! (Functionality to be added)")