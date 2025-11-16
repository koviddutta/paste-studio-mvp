import reflex as rx
from reflex_monaco import monaco
from app.states.paste_state import PasteState
from app.components.header import header


def metadata_item(icon: str, text: rx.Var | str) -> rx.Component:
    """A component to display a piece of metadata with an icon."""
    return rx.el.div(
        rx.icon(icon, class_name="h-4 w-4 text-gray-500"),
        rx.el.span(text, class_name="text-sm font-medium text-gray-700"),
        class_name="flex items-center gap-2",
    )


def delete_confirmation_dialog() -> rx.Component:
    """Confirmation dialog for deleting a paste."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(rx.el.div()),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                "Confirm Deletion", class_name="text-lg font-semibold"
            ),
            rx.radix.primitives.dialog.description(
                "Are you sure you want to delete this paste? This action cannot be undone.",
                class_name="my-4 text-gray-600",
            ),
            rx.el.div(
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        "Cancel",
                        on_click=PasteState.cancel_delete,
                        class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors",
                    )
                ),
                rx.el.button(
                    "Delete Paste",
                    on_click=PasteState.delete_paste,
                    class_name="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors",
                ),
                class_name="flex justify-end gap-4 mt-4",
            ),
            style={
                "max_width": "450px",
                "border_radius": "12px",
                "padding": "24px",
                "background_color": "white",
                "box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            },
        ),
        open=PasteState.show_delete_dialog,
    )


def skeleton_loader() -> rx.Component:
    """A skeleton loader for the paste view."""
    return rx.el.div(
        rx.el.div(class_name="h-16 bg-gray-200 rounded-t-2xl animate-pulse"),
        rx.el.div(class_name="h-80 bg-gray-200/80 animate-pulse"),
        class_name="w-full max-w-4xl border border-gray-200 rounded-2xl shadow-sm overflow-hidden",
    )


def paste_view() -> rx.Component:
    """The main view for displaying a paste's content and metadata."""
    return rx.el.div(
        rx.cond(
            PasteState.is_loading,
            skeleton_loader(),
            rx.cond(
                PasteState.current_paste,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            metadata_item(
                                "file-code-2",
                                PasteState.current_paste["language"].capitalize(),
                            ),
                            metadata_item(
                                "calendar-clock",
                                f"Created: {PasteState.current_paste['created_at'].to_string()[:16].replace('T', ' ')} UTC",
                            ),
                            rx.cond(
                                PasteState.current_paste["expires_at"],
                                metadata_item(
                                    "timer-off",
                                    f"Expires: {PasteState.current_paste['expires_at'].to_string()[:16].replace('T', ' ')} UTC",
                                ),
                                metadata_item("infinity", "Expires: Never"),
                            ),
                            class_name="flex flex-wrap items-center gap-4 md:gap-6",
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon("copy", class_name="h-4 w-4 mr-2"),
                                "Copy",
                                on_click=[
                                    rx.set_clipboard(
                                        PasteState.current_paste["content"]
                                    ),
                                    rx.toast.success("Copied to clipboard!"),
                                ],
                                class_name="flex items-center px-4 py-2 text-sm font-semibold text-gray-800 bg-gray-100 rounded-lg hover:bg-gray-200 transition-all active:scale-95",
                            ),
                            rx.el.button(
                                rx.icon("trash-2", class_name="h-4 w-4 mr-2"),
                                "Delete",
                                on_click=PasteState.confirm_delete,
                                class_name="flex items-center px-4 py-2 text-sm font-semibold text-red-600 bg-red-100 rounded-lg hover:bg-red-200 transition-all active:scale-95",
                            ),
                            class_name="flex items-center gap-3",
                        ),
                        class_name="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-4 border-b border-gray-200",
                    ),
                    monaco(
                        value=PasteState.current_paste["content"],
                        language=PasteState.current_paste["language"],
                        theme="vs-dark",
                        height="60vh",
                        options={"readOnly": True, "minimap": {"enabled": False}},
                    ),
                    class_name="w-full max-w-4xl bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden",
                ),
                rx.el.div(
                    rx.el.p(
                        "Paste not found or has expired.",
                        class_name="text-lg text-gray-600",
                    ),
                    rx.el.a(
                        "Create a new paste",
                        href="/",
                        class_name="text-purple-600 hover:underline",
                    ),
                    class_name="flex flex-col items-center justify-center h-64 space-y-4",
                ),
            ),
        )
    )


def view_paste_page() -> rx.Component:
    """The full page for viewing a paste."""
    return rx.el.main(
        header(),
        delete_confirmation_dialog(),
        rx.el.div(
            paste_view(),
            class_name="flex flex-col items-center justify-start w-full min-h-[calc(100vh-65px)] p-4 sm:p-6 lg:p-8",
        ),
        class_name="font-['Inter'] bg-gray-50",
    )