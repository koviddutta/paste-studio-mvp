import reflex as rx
from app.components.header import header
from app.components.footer import footer
from app.components.recipe_search import recipe_search
from app.components.formulation_display import formulation_display
from app.states.formulation_state import FormulationState


def index() -> rx.Component:
    return rx.el.div(
        header(),
        rx.el.main(
            rx.el.div(
                rx.el.h2(
                    "New Formulation",
                    class_name="text-xl font-semibold text-gray-900 mb-6",
                ),
                recipe_search(),
                rx.el.div(class_name="h-8"),
                formulation_display(),
                class_name="container mx-auto px-4 py-8 max-w-6xl",
            ),
            class_name="flex-1 bg-gray-50 min-h-screen",
        ),
        footer(),
        class_name="flex flex-col min-h-screen",
    )


app = rx.App(theme=rx.theme(appearance="light"))
app.add_page(index, route="/", title="Paste Studio - Indian Sweets Formulation")