import reflex as rx
from typing import TypedDict, Optional, Literal
from app.states.formulation_state import RecipeIngredient, FormulationResult


class ClassInfo(TypedDict):
    icon: str
    color: str
    text_color: str
    bg_color: str
    border_color: str


CLASS_STYLES: dict[str, ClassInfo] = {
    "A_DAIRY": {
        "icon": "milk",
        "color": "blue",
        "text_color": "text-blue-800",
        "bg_color": "bg-blue-100",
        "border_color": "border-blue-200",
    },
    "B_NUT": {
        "icon": "nut",
        "color": "amber",
        "text_color": "text-amber-800",
        "bg_color": "bg-amber-100",
        "border_color": "border-amber-200",
    },
    "C_SUGAR": {
        "icon": "candy",
        "color": "pink",
        "text_color": "text-pink-800",
        "bg_color": "bg-pink-100",
        "border_color": "border-pink-200",
    },
    "D_FAT": {
        "icon": "flask-conical",
        "color": "yellow",
        "text_color": "text-yellow-800",
        "bg_color": "bg-yellow-100",
        "border_color": "border-yellow-200",
    },
    "E_STABILIZER": {
        "icon": "test-tube-2",
        "color": "purple",
        "text_color": "text-purple-800",
        "bg_color": "bg-purple-100",
        "border_color": "border-purple-200",
    },
    "F_AROMATIC": {
        "icon": "sprout",
        "color": "green",
        "text_color": "text-green-800",
        "bg_color": "bg-green-100",
        "border_color": "border-green-200",
    },
    "G_GRAIN": {
        "icon": "wheat",
        "color": "orange",
        "text_color": "text-orange-800",
        "bg_color": "bg-orange-100",
        "border_color": "border-orange-200",
    },
    "H_SEED": {
        "icon": "seedling",
        "color": "stone",
        "text_color": "text-stone-800",
        "bg_color": "bg-stone-100",
        "border_color": "border-stone-200",
    },
    "UNKNOWN": {
        "icon": "help-circle",
        "color": "gray",
        "text_color": "text-gray-800",
        "bg_color": "bg-gray-100",
        "border_color": "border-gray-200",
    },
}


def _class_badge(class_name: rx.Var[str]) -> rx.Component:
    """Renders a small, color-coded badge for an ingredient class."""
    color_map = [
        (
            name,
            f"px-2 py-0.5 text-xs font-semibold rounded-full {style['text_color']} {style['bg_color']}",
        )
        for name, style in CLASS_STYLES.items()
    ]
    default_style = CLASS_STYLES["UNKNOWN"]
    default_class = f"px-2 py-0.5 text-xs font-semibold rounded-full {default_style['text_color']} {default_style['bg_color']}"
    return rx.el.span(
        class_name.replace("_", " "),
        class_name=rx.match(class_name, *color_map, default_class),
    )


def ingredient_distribution_card() -> rx.Component:
    """Displays a grid of ingredient class counts."""

    def render_class_item(class_name: str):
        from app.states.formulation_state import FormulationState

        style = CLASS_STYLES.get(class_name, CLASS_STYLES["UNKNOWN"])
        count = FormulationState.ingredient_distribution.get(class_name, 0)
        return rx.el.div(
            rx.el.div(
                rx.icon(style["icon"], class_name=f"h-6 w-6 {style['text_color']}"),
                class_name=f"p-2 {style['bg_color']} rounded-lg",
            ),
            rx.el.div(
                rx.el.p(
                    class_name.replace("_", " ").capitalize(),
                    class_name="text-sm font-medium text-gray-500",
                ),
                rx.el.p(count, class_name="text-xl font-bold text-gray-800"),
                class_name="flex flex-col",
            ),
            class_name="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-xl shadow-sm w-full",
        )

    return rx.el.div(
        rx.el.h3(
            "Ingredient Class Distribution",
            class_name="text-xl font-semibold text-gray-800 mb-4",
        ),
        rx.el.div(
            rx.foreach(list(CLASS_STYLES.keys())[:-1], render_class_item),
            class_name="grid grid-cols-2 md:grid-cols-3 gap-4",
        ),
        class_name="w-full",
    )


def classified_ingredients_list() -> rx.Component:
    """Displays a list of ingredients, grouped by their processing class."""
    from app.states.formulation_state import FormulationState

    result = FormulationState.formulation_result

    def render_ingredient_row(ingredient: RecipeIngredient) -> rx.Component:
        class_name = ingredient["classified_data"]["class_name"]
        style = CLASS_STYLES.get(class_name, CLASS_STYLES["UNKNOWN"])
        return rx.el.tr(
            rx.el.td(ingredient["name"], class_name="px-4 py-3 text-sm font-medium"),
            rx.el.td(f"{ingredient['mass_g']:.2f}g", class_name="px-4 py-3 text-sm"),
            rx.el.td(_class_badge(class_name), class_name="px-4 py-3"),
            class_name=f"{style['bg_color']} {style['text_color']}",
        )

    return rx.cond(
        result,
        rx.el.div(
            rx.el.h3(
                "Classified Ingredients",
                class_name="text-xl font-semibold text-gray-800 mb-4",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("Ingredient", class_name="text-left p-3"),
                            rx.el.th("Quantity", class_name="text-left p-3"),
                            rx.el.th("Class", class_name="text-left p-3"),
                            class_name="bg-gray-50",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(result["ingredients"], render_ingredient_row)
                    ),
                    class_name="w-full table-auto",
                ),
                class_name="w-full overflow-hidden border border-gray-200 rounded-xl max-h-[600px] overflow-y-auto",
            ),
            class_name="w-full",
        ),
        rx.el.div(),
    )