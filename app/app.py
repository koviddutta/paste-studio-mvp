import reflex as rx
from app.components.header import header
from app.components.paste_form import paste_form


def index() -> rx.Component:
    """The main page of the Paste Studio app."""
    return rx.el.main(
        header(),
        rx.el.div(
            paste_form(),
            class_name="flex flex-col items-center justify-start w-full min-h-[calc(100vh-65px)] p-4 sm:p-6 lg:p-8",
        ),
        class_name="font-['Inter'] bg-gray-50",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")