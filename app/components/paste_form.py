import reflex as rx
from app.states.paste_state import PasteState


def language_selector() -> rx.Component:
    """Dropdown to select the programming language."""
    return rx.el.div(
        rx.el.label(
            "Language",
            html_for="language",
            class_name="text-sm font-medium text-gray-600",
        ),
        rx.el.select(
            rx.foreach(
                PasteState.languages,
                lambda lang: rx.el.option(lang.capitalize(), value=lang),
            ),
            id="language",
            value=PasteState.language,
            on_change=PasteState.set_language,
            class_name="w-full mt-1 px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all text-sm",
        ),
        class_name="w-full md:w-auto",
    )


def expiration_selector() -> rx.Component:
    """Segmented control to select paste expiration."""
    return rx.el.div(
        rx.el.label("Expires In", class_name="text-sm font-medium text-gray-600 mb-2"),
        rx.el.div(
            rx.foreach(
                PasteState.expiration_options,
                lambda option: rx.el.button(
                    option["label"],
                    on_click=lambda: PasteState.set_expiration(option["value"]),
                    class_name=rx.cond(
                        PasteState.expiration == option["value"],
                        "flex-1 px-3 py-2 text-sm font-semibold text-white bg-purple-600 rounded-md shadow-sm transition-all",
                        "flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white hover:bg-gray-100 rounded-md transition-colors",
                    ),
                    type="button",
                ),
            ),
            class_name="flex items-center p-1 space-x-1 bg-gray-200 rounded-lg w-full",
        ),
        class_name="w-full",
    )


def action_buttons() -> rx.Component:
    """Action buttons for creating, clearing, and settings."""
    return rx.el.div(
        rx.el.button(
            rx.icon("settings-2", class_name="h-4 w-4"),
            on_click=PasteState.show_settings,
            class_name="p-2 text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-all",
            type="button",
        ),
        rx.el.div(
            rx.el.button(
                "Clear",
                on_click=PasteState.clear_content,
                class_name="px-5 py-2.5 text-sm font-semibold text-gray-800 bg-gray-200 rounded-lg hover:bg-gray-300 transition-all active:scale-95",
                type="button",
            ),
            rx.el.button(
                "Create Paste",
                on_click=PasteState.create_paste,
                class_name="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-md hover:shadow-lg hover:from-purple-700 hover:to-indigo-700 transition-all active:scale-95",
                type="submit",
            ),
            class_name="flex items-center gap-3",
        ),
        class_name="flex items-center justify-between w-full",
    )


def paste_form() -> rx.Component:
    """The main form for creating a new paste."""
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.el.textarea(
                    placeholder="Paste your code or text here...",
                    on_change=PasteState.set_content,
                    class_name="w-full h-96 p-4 font-mono text-sm bg-gray-50 border border-gray-200 rounded-xl shadow-inner focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all",
                    required=True,
                    default_value=PasteState.content,
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.div(expiration_selector(), class_name="w-full md:max-w-xs"),
                language_selector(),
                class_name="flex flex-col md:flex-row gap-6 md:gap-4 items-start md:items-end mb-8",
            ),
            action_buttons(),
            class_name="w-full",
        ),
        class_name="w-full max-w-3xl p-6 md:p-8 bg-white border border-gray-200 rounded-2xl shadow-sm",
    )