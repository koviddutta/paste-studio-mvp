import reflex as rx
from typing import Literal, TypedDict, Optional
import uuid
from datetime import datetime, timedelta, timezone
import logging
import asyncio

Expiration = Literal["1h", "1d", "1w", "never"]


class Paste(TypedDict):
    """A paste with its content and metadata."""

    id: str
    content: str
    language: str
    created_at: str
    expires_at: Optional[str]


class PasteState(rx.State):
    """Manages the state for creating and viewing pastes."""

    content: str = ""
    language: str = "python"
    expiration: Expiration = "1d"
    pastes: dict[str, Paste] = {}
    current_paste: Optional[Paste] = None
    is_loading: bool = False
    show_delete_dialog: bool = False
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
    def on_load(self):
        return PasteState.periodic_cleanup

    @rx.var
    def recent_pastes(self) -> list[Paste]:
        """Returns the 5 most recent, non-expired pastes."""
        now_utc = datetime.now(timezone.utc).isoformat()
        all_pastes = sorted(
            self.pastes.values(), key=lambda p: p["created_at"], reverse=True
        )
        valid_pastes = [
            p for p in all_pastes if not p["expires_at"] or p["expires_at"] > now_utc
        ]
        return valid_pastes[:5]

    @rx.event
    def create_paste(self):
        """Creates a new paste, stores it, and redirects to its page."""
        if not self.content.strip():
            return rx.toast.error("Paste content cannot be empty.")
        paste_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc)
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
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
        }
        self.pastes[paste_id] = new_paste
        self.content = ""
        yield rx.toast.success("Paste created successfully!")
        return rx.redirect(f"/paste/{paste_id}")

    @rx.event
    def load_paste(self):
        """Loads a paste by its ID from the URL parameter."""
        self.is_loading = True
        self.current_paste = None
        try:
            paste_id = self.router.page.params.get("paste_id", "")
        except Exception as e:
            logging.exception(f"Error getting paste_id: {e}")
            paste_id = ""
        if not paste_id:
            self.is_loading = False
            return rx.toast.error("Invalid paste ID.")
        paste = self.pastes.get(paste_id)
        if not paste:
            self.is_loading = False
            return rx.toast.error("Paste not found.")
        if paste.get("expires_at") and datetime.fromisoformat(
            paste["expires_at"]
        ) < datetime.now(timezone.utc):
            del self.pastes[paste_id]
            self.is_loading = False
            return rx.toast.warning("This paste has expired.")
        self.current_paste = paste
        self.is_loading = False

    @rx.event
    def clear_content(self):
        """Clears the textarea content."""
        self.content = ""

    @rx.event
    def show_settings(self):
        """Placeholder for showing settings."""
        return rx.toast.info("Settings clicked! (Functionality to be added)")

    def _close_dialog(self):
        self.show_delete_dialog = False

    @rx.event
    def confirm_delete(self):
        """Displays the delete confirmation dialog."""
        self.show_delete_dialog = True

    @rx.event
    def cancel_delete(self):
        """Closes the delete confirmation dialog."""
        self.show_delete_dialog = False

    @rx.event
    def delete_paste(self):
        """Deletes the current paste and redirects to home."""
        if self.current_paste:
            paste_id = self.current_paste["id"]
            if paste_id in self.pastes:
                del self.pastes[paste_id]
        self._close_dialog()
        yield rx.toast.success("Paste deleted.")
        return rx.redirect("/")

    @rx.event(background=True)
    async def periodic_cleanup(self):
        """Periodically cleans up expired pastes."""
        while True:
            async with self:
                now = datetime.now(timezone.utc)
                expired_ids = [
                    pid
                    for pid, paste in self.pastes.items()
                    if paste.get("expires_at")
                    and datetime.fromisoformat(paste["expires_at"]) < now
                ]
                for pid in expired_ids:
                    del self.pastes[pid]
                if expired_ids:
                    logging.info(f"Cleaned up {len(expired_ids)} expired pastes.")
            await asyncio.sleep(60)