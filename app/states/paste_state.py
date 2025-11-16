import reflex as rx
from typing import Literal

Expiration = Literal["1h", "1d", "1w", "never"]


class PasteState(rx.State):
    """Manages the state for creating and viewing pastes."""

    content: str = ""
    language: str = "python"
    expiration: Expiration = "1d"
    is_loading: bool = False
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
        """Creates a new paste."""
        if not self.content.strip():
            return rx.toast.error("Paste content cannot be empty.")
        yield rx.toast.info(
            f"Creating paste with language '{self.language}' and expiration '{self.expiration}'."
        )

    @rx.event
    def clear_content(self):
        """Clears the textarea content."""
        self.content = ""

    @rx.event
    def show_settings(self):
        """Placeholder for showing settings."""
        return rx.toast.info("Settings clicked! (Functionality to be added)")