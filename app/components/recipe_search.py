import reflex as rx
from app.states.formulation_state import FormulationState


def recipe_search() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                "Search Recipe",
                class_name="block text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="e.g. Gulab Jamun, Mysore Pak...",
                    on_change=FormulationState.handle_search,
                    class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-violet-500 focus:ring-violet-500 py-3 px-4",
                    default_value=FormulationState.search_query,
                ),
                rx.cond(
                    FormulationState.search_results.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            FormulationState.search_results,
                            lambda r: rx.el.button(
                                r["name"],
                                on_click=lambda: FormulationState.select_recipe(r),
                                class_name="w-full text-left px-4 py-2 hover:bg-violet-50 text-sm text-gray-700",
                            ),
                        ),
                        class_name="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-100 max-h-60 overflow-auto z-20",
                    ),
                ),
                class_name="relative",
            ),
            class_name="flex-1",
        ),
        rx.el.div(
            rx.el.label(
                "Batch Size (kg)",
                class_name="block text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.input(
                type="number",
                default_value="1.0",
                on_change=lambda v: FormulationState.set_batch_size(v.to(float)),
                class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-violet-500 focus:ring-violet-500 py-3 px-4",
            ),
            class_name="w-32",
        ),
        rx.el.div(
            rx.el.button(
                rx.cond(
                    FormulationState.is_generating,
                    rx.el.span("Processing...", class_name="animate-pulse"),
                    rx.el.span("Generate Formulation"),
                ),
                on_click=FormulationState.generate_formulation,
                disabled=FormulationState.is_generating,
                class_name="w-full bg-violet-600 text-white rounded-lg px-6 py-3 font-medium hover:bg-violet-700 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed h-[46px] mt-6",
            )
        ),
        class_name="flex gap-4 items-start bg-white p-6 rounded-xl shadow-sm border border-gray-100",
    )