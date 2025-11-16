import reflex as rx


def header() -> rx.Component:
    """Renders the application header."""
    return rx.el.header(
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.icon("flask-conical", class_name="h-7 w-7 text-purple-600"),
                    rx.el.span(
                        "Formulation Studio",
                        class_name="text-xl font-bold text-gray-800 tracking-tighter",
                    ),
                    class_name="flex items-center gap-3",
                ),
                href="/",
            ),
            rx.el.div(
                rx.el.a(
                    "Docs",
                    href="#",
                    class_name="px-3 py-1.5 text-sm font-medium text-gray-500 hover:text-gray-800 transition-colors",
                ),
                rx.el.a(
                    rx.icon(
                        "github",
                        class_name="h-5 w-5 text-gray-500 hover:text-gray-800 transition-colors",
                    ),
                    href="https://github.com/reflex-dev/reflex",
                    target="_blank",
                ),
                class_name="flex items-center gap-4",
            ),
            class_name="flex items-center justify-between h-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
        ),
        class_name="w-full border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-40",
    )