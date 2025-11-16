import reflex as rx
from app.states.paste_state import PasteState
from app.components.header import header


def metadata_item(icon: str, text: rx.Var | str) -> rx.Component:
    """A component to display a piece of metadata with an icon."""
    return rx.el.div(
        rx.icon(icon, class_name="h-4 w-4 text-gray-500"),
        rx.el.span(text, class_name="text-sm font-medium text-gray-700"),
        class_name="flex items-center gap-2",
    )


def paste_view() -> rx.Component:
    """The main view for displaying a paste's content and metadata."""
    return rx.el.div(
        rx.cond(
            PasteState.current_paste,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        metadata_item(
                            "file_code_2",
                            PasteState.current_paste["language"].capitalize(),
                        ),
                        metadata_item(
                            "calendar-clock",
                            f"Created at: {PasteState.current_paste['created_at'].to_string()[:19]} UTC",
                        ),
                        rx.cond(
                            PasteState.current_paste["expires_at"],
                            metadata_item(
                                "timer-off",
                                f"Expires at: {PasteState.current_paste['expires_at'].to_string()[:19]} UTC",
                            ),
                            metadata_item("infinity", "Expires: Never"),
                        ),
                        class_name="flex flex-wrap items-center gap-4 md:gap-6",
                    ),
                    rx.el.button(
                        rx.icon("copy", class_name="h-4 w-4 mr-2"),
                        "Copy",
                        on_click=[
                            rx.set_clipboard(PasteState.current_paste["content"]),
                            rx.toast.success("Copied to clipboard!"),
                        ],
                        class_name="flex items-center px-4 py-2 text-sm font-semibold text-gray-800 bg-gray-100 rounded-lg hover:bg-gray-200 transition-all active:scale-95",
                    ),
                    class_name="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 border-b border-gray-200",
                ),
                rx.el.pre(
                    rx.el.code(
                        PasteState.current_paste["content"],
                        class_name="language-{PasteState.current_paste['language']}",
                    ),
                    class_name="w-full p-4 font-mono text-sm bg-gray-50/50 overflow-x-auto",
                ),
                class_name="w-full max-w-4xl bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden",
            ),
            rx.el.div(
                rx.el.p(
                    "Paste not found or has expired.",
                    class_name="text-lg text-gray-600",
                ),
                class_name="flex items-center justify-center h-64",
            ),
        )
    )


def view_paste_page() -> rx.Component:
    """The full page for viewing a paste."""
    return rx.el.main(
        header(),
        rx.el.div(
            paste_view(),
            class_name="flex flex-col items-center justify-start w-full min-h-[calc(100vh-65px)] p-4 sm:p-6 lg:p-8",
        ),
        class_name="font-['Inter'] bg-gray-50",
    )