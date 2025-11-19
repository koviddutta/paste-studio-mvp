import reflex as rx
from app.components.header import header
from app.components.recipe_search import recipe_search_page
from app.states.formulation_state import FormulationState


def index() -> rx.Component:
    """The main page for the Formulation Engine."""
    return rx.el.main(
        header(), recipe_search_page(), class_name="font-['Inter'] bg-gray-50"
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
app.add_page(index, route="/", title="Indian Sweets Formulation Engine")
app.add_page(
    lambda: rx.fragment(
        rx.script("window.location.href = 'https://github.com/reflex-dev/reflex'")
    ),
    route="/docs",
)