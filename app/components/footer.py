import reflex as rx


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.p(
                "© 2024 Paste Studio MVP. Released under the MIT License.",
                class_name="text-sm text-gray-500",
            ),
            rx.el.div(
                rx.el.a(
                    "GitHub",
                    href="https://github.com/koviddutta/paste-studio-mvp",
                    target="_blank",
                    rel="noopener noreferrer",
                    class_name="text-gray-400 hover:text-gray-600 transition-colors",
                ),
                rx.el.span("•", class_name="text-gray-300"),
                rx.el.a(
                    "License",
                    href="https://opensource.org/licenses/MIT",
                    target="_blank",
                    rel="noopener noreferrer",
                    class_name="text-gray-400 hover:text-gray-600 transition-colors",
                ),
                class_name="flex gap-4 text-sm",
            ),
            class_name="container mx-auto px-4 py-6 flex flex-col md:flex-row justify-between items-center gap-4",
        ),
        class_name="bg-white border-t border-gray-100 mt-auto w-full",
    )