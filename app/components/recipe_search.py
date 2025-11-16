import reflex as rx
from app.states.formulation_state import FormulationState
from .formulation_display import formulation_results_display


def search_input() -> rx.Component:
    """The search bar with autocomplete results."""
    return rx.el.div(
        rx.el.div(
            rx.icon("search", class_name="h-5 w-5 text-gray-400"),
            rx.el.input(
                placeholder="Search for an Indian sweet (e.g., Gulab Jamun)",
                on_change=FormulationState.on_search_query_change.debounce(300),
                class_name="w-full bg-transparent focus:outline-none text-gray-800 placeholder-gray-500",
                default_value=FormulationState.search_query,
            ),
            rx.cond(
                FormulationState.is_searching,
                rx.el.div(rx.spinner(class_name="h-5 w-5 text-purple-500")),
            ),
            class_name="flex items-center w-full gap-3",
        ),
        rx.cond(
            FormulationState.search_results.length() > 0,
            rx.el.ul(
                rx.foreach(
                    FormulationState.search_results,
                    lambda result: rx.el.li(
                        rx.el.button(
                            result["name"],
                            on_click=lambda: FormulationState.select_recipe(
                                result["name"]
                            ),
                            class_name="w-full text-left p-2 hover:bg-gray-100 rounded-md text-sm",
                        )
                    ),
                ),
                class_name="absolute top-full left-0 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto",
            ),
        ),
        class_name="relative w-full max-w-2xl mx-auto p-4 border border-gray-300 rounded-xl bg-white shadow-sm",
    )


def batch_size_input() -> rx.Component:
    """Input for setting the batch size."""
    return rx.el.div(
        rx.el.label(
            "Batch Size (kg)",
            html_for="batch_size",
            class_name="text-sm font-medium text-gray-700",
        ),
        rx.el.input(
            id="batch_size",
            type="number",
            default_value=FormulationState.batch_size_kg.to_string(),
            on_change=FormulationState.set_batch_size_kg,
            class_name="mt-1 w-full md:w-48 px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all text-sm",
            step="0.1",
            min="0.1",
        ),
        class_name="flex flex-col items-center",
    )


def generate_button() -> rx.Component:
    """The button to trigger formulation generation."""
    return rx.el.button(
        rx.cond(
            FormulationState.is_generating,
            rx.el.div(rx.spinner(class_name="h-5 w-5 text-white"), "Generating..."),
            rx.el.div(
                rx.icon("flask-conical", class_name="h-5 w-5"), "Generate Formulation"
            ),
        ),
        on_click=FormulationState.generate_formulation,
        disabled=FormulationState.is_generating
        | (FormulationState.selected_recipe_name == ""),
        class_name="flex items-center justify-center gap-2 px-6 py-3 text-base font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-md hover:shadow-lg hover:from-purple-700 hover:to-indigo-700 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
    )


def recipe_search_page() -> rx.Component:
    """The main page for searching recipes and generating formulations."""
    return rx.el.main(
        rx.el.div(
            rx.el.h1(
                "Indian Sweets Formulation Engine",
                class_name="text-4xl font-bold text-gray-800 tracking-tighter",
            ),
            rx.el.p(
                "Search from over 1,000 traditional recipes to generate a production-ready formulation.",
                class_name="text-lg text-gray-600 max-w-2xl text-center",
            ),
            class_name="flex flex-col items-center gap-4 text-center mb-12",
        ),
        search_input(),
        rx.el.div(batch_size_input(), class_name="mt-8"),
        rx.el.div(generate_button(), class_name="mt-8"),
        formulation_results_display(),
        class_name="flex flex-col items-center justify-start w-full min-h-screen p-4 sm:p-6 lg:p-8",
    )