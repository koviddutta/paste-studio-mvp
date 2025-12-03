import reflex as rx


def header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.icon("flask-conical", class_name="h-8 w-8 text-violet-600"),
                rx.el.h1("Paste Studio", class_name="text-2xl font-bold text-gray-900"),
                class_name="flex items-center gap-3",
            ),
            rx.el.nav(
                rx.el.a(
                    "Formulation",
                    href="/",
                    class_name="text-sm font-medium text-gray-700 hover:text-violet-600",
                ),
                rx.el.a(
                    "Paste Studio",
                    href="/paste-studio",
                    class_name="text-sm font-medium text-gray-700 hover:text-violet-600",
                ),
                rx.el.a(
                    "Library",
                    href="#",
                    class_name="text-sm font-medium text-gray-500 cursor-not-allowed",
                ),
                rx.el.a(
                    "Settings",
                    href="#",
                    class_name="text-sm font-medium text-gray-500 cursor-not-allowed",
                ),
                class_name="flex gap-6",
            ),
            class_name="container mx-auto px-4 h-16 flex items-center justify-between",
        ),
        class_name="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50",
    )