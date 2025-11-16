import reflex as rx
from app.states.paste_state import PasteState


def recent_paste_card(paste: rx.Var[dict]) -> rx.Component:
    """A card to display a single recent paste."""
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.icon("file-code-2", class_name="h-4 w-4 text-gray-500"),
                rx.el.span(
                    paste["language"].capitalize(),
                    class_name="text-sm font-medium text-gray-800",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.span(
                f"Created {paste['created_at'].to_string()[:16].replace('T', ' ')} UTC",
                class_name="text-xs text-gray-500",
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.p(
            paste["content"].to_string()[:100]
            + rx.cond(paste["content"].length() > 100, "...", ""),
            class_name="mt-2 text-sm text-gray-600 font-mono line-clamp-2",
        ),
        href=f"/paste/{paste['id']}",
        class_name="block w-full p-4 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all",
    )


def recent_pastes_section() -> rx.Component:
    """A section to display the 5 most recent pastes."""
    return rx.el.div(
        rx.el.h2(
            "Recent Pastes", class_name="text-xl font-bold text-gray-800 tracking-tight"
        ),
        rx.cond(
            PasteState.recent_pastes.length() > 0,
            rx.el.div(
                rx.foreach(PasteState.recent_pastes, recent_paste_card),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4",
            ),
            rx.el.div(
                rx.el.p(
                    "No recent pastes. Create one to get started!",
                    class_name="text-gray-500",
                ),
                class_name="flex items-center justify-center h-24 mt-4 border-2 border-dashed border-gray-300 rounded-xl",
            ),
        ),
        class_name="w-full max-w-3xl",
    )