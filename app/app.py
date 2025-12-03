import reflex as rx
from app.components.header import header
from app.components.footer import footer
from app.components.recipe_search import recipe_search
from app.components.formulation_display import formulation_display
from app.states.formulation_state import FormulationState
from app.states.paste_studio_state import PasteStudioState


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


def validation_badge(status: str) -> rx.Component:
    return rx.cond(
        status == "PASS",
        rx.el.span(
            "PASS",
            class_name="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full",
        ),
        rx.cond(
            status == "WARNING",
            rx.el.span(
                "WARNING",
                class_name="bg-amber-100 text-amber-700 text-xs font-bold px-2 py-1 rounded-full",
            ),
            rx.el.span(
                "FAIL",
                class_name="bg-red-100 text-red-700 text-xs font-bold px-2 py-1 rounded-full",
            ),
        ),
    )


def metric_card(label: str, value: str, subtext: str) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-sm text-gray-500 font-medium"),
        rx.el.p(value, class_name="text-2xl font-bold text-gray-900 mt-1"),
        rx.el.p(subtext, class_name="text-xs text-gray-400 mt-1"),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm",
    )


def paste_studio() -> rx.Component:
    return rx.el.div(
        header(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(
                    "Paste Studio Engine",
                    class_name="text-3xl font-bold text-gray-900 mb-8",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                "Configuration", class_name="text-xl font-semibold mb-6"
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Search Sweet",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    placeholder="e.g. Gulab Jamun...",
                                    on_change=PasteStudioState.search_sweets,
                                    class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-violet-500 focus:ring-violet-500 py-2 px-3",
                                    default_value=PasteStudioState.search_query,
                                ),
                                rx.cond(
                                    PasteStudioState.search_results.length() > 0,
                                    rx.el.div(
                                        rx.foreach(
                                            PasteStudioState.search_results,
                                            lambda res: rx.el.button(
                                                rx.el.div(
                                                    rx.el.span(
                                                        res["sweet_name"],
                                                        class_name="font-medium",
                                                    ),
                                                    rx.el.span(
                                                        res["category"],
                                                        class_name="text-xs text-gray-500 ml-2",
                                                    ),
                                                ),
                                                on_click=lambda: PasteStudioState.select_sweet(
                                                    res
                                                ),
                                                class_name="w-full text-left px-4 py-2 hover:bg-violet-50 text-sm text-gray-700 border-b last:border-0",
                                            ),
                                        ),
                                        class_name="absolute z-10 w-full mt-1 bg-white rounded-lg shadow-lg border border-gray-100 max-h-60 overflow-auto",
                                    ),
                                ),
                                class_name="relative mb-6",
                            ),
                            rx.cond(
                                PasteStudioState.selected_sweet,
                                rx.el.div(
                                    rx.icon(
                                        "check_check",
                                        class_name="h-5 w-5 text-violet-600",
                                    ),
                                    rx.el.div(
                                        rx.el.p(
                                            "Selected Sweet",
                                            class_name="text-xs text-gray-500 uppercase font-bold",
                                        ),
                                        rx.el.p(
                                            PasteStudioState.selected_sweet[
                                                "sweet_name"
                                            ],
                                            class_name="font-bold text-gray-900",
                                        ),
                                    ),
                                    class_name="flex items-center gap-3 bg-violet-50 p-4 rounded-xl border border-violet-100 mb-6",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Base Profile",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.select(
                                    rx.el.option("White Base", value="white"),
                                    rx.el.option("Kulfi Base", value="kulfi"),
                                    rx.el.option("Chocolate Base", value="chocolate"),
                                    on_change=PasteStudioState.set_base,
                                    value=PasteStudioState.selected_base,
                                    class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-violet-500 focus:ring-violet-500 py-2 px-3",
                                ),
                                class_name="mb-4",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Batch Weight (g)",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    type="number",
                                    default_value="1000",
                                    on_change=lambda v: PasteStudioState.set_batch_weight(
                                        v.to(float)
                                    ),
                                    class_name="w-full rounded-lg border-gray-300 shadow-sm focus:border-violet-500 focus:ring-violet-500 py-2 px-3",
                                ),
                                class_name="mb-6",
                            ),
                            rx.el.button(
                                rx.cond(
                                    PasteStudioState.is_loading,
                                    rx.el.span(
                                        "Processing...", class_name="animate-pulse"
                                    ),
                                    "Design Paste & Infusion",
                                ),
                                on_click=PasteStudioState.run_paste_engine,
                                disabled=PasteStudioState.is_loading,
                                class_name="w-full bg-violet-600 text-white rounded-xl px-6 py-3 font-bold hover:bg-violet-700 transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed",
                            ),
                            rx.cond(
                                PasteStudioState.error_message,
                                rx.el.div(
                                    PasteStudioState.error_message,
                                    class_name="mt-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-100",
                                ),
                            ),
                            class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-100",
                        ),
                        class_name="w-full lg:w-1/3",
                    ),
                    rx.el.div(
                        rx.cond(
                            PasteStudioState.paste_result,
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.h2(
                                            PasteStudioState.paste_result["sweet_name"],
                                            class_name="text-2xl font-bold text-gray-900",
                                        ),
                                        rx.el.span(
                                            "+", class_name="text-gray-400 text-xl"
                                        ),
                                        rx.el.h2(
                                            PasteStudioState.paste_result["base_name"],
                                            class_name="text-2xl font-bold text-gray-900",
                                        ),
                                        class_name="flex items-center gap-3 mb-2",
                                    ),
                                    rx.el.div(
                                        rx.el.span(
                                            "Composition: ",
                                            class_name="text-gray-500 font-medium",
                                        ),
                                        rx.el.span(
                                            PasteStudioState.paste_result[
                                                "sweet_pct"
                                            ].to_string()
                                            + "% Sweet",
                                            class_name="font-bold text-violet-600",
                                        ),
                                        rx.el.span(
                                            " / ", class_name="text-gray-300 mx-2"
                                        ),
                                        rx.el.span(
                                            PasteStudioState.paste_result[
                                                "base_pct"
                                            ].to_string()
                                            + "% Base",
                                            class_name="font-bold text-gray-700",
                                        ),
                                        class_name="mb-8",
                                    ),
                                    rx.el.div(
                                        metric_card(
                                            "Sugar",
                                            PasteStudioState.paste_result["metrics"][
                                                "sugar_pct"
                                            ].to_string()
                                            + "%",
                                            "Target: 20-40%",
                                        ),
                                        metric_card(
                                            "Fat",
                                            PasteStudioState.paste_result["metrics"][
                                                "fat_pct"
                                            ].to_string()
                                            + "%",
                                            "Target: 10-20%",
                                        ),
                                        metric_card(
                                            "Total Solids",
                                            PasteStudioState.paste_result["metrics"][
                                                "solids_pct"
                                            ].to_string()
                                            + "%",
                                            "Target: 55-70%",
                                        ),
                                        metric_card(
                                            "Water Activity",
                                            PasteStudioState.paste_result["metrics"][
                                                "water_activity"
                                            ].to_string(),
                                            "Optimal: 0.68-0.75",
                                        ),
                                        class_name="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8",
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            rx.el.h3(
                                                "Validation Report",
                                                class_name="text-lg font-bold text-gray-900 mb-4",
                                            ),
                                            rx.el.div(
                                                rx.foreach(
                                                    PasteStudioState.paste_result[
                                                        "validation"
                                                    ]["parameters"],
                                                    lambda param: rx.el.div(
                                                        rx.el.div(
                                                            rx.el.span(
                                                                param["name"],
                                                                class_name="font-medium text-gray-700 text-sm",
                                                            ),
                                                            validation_badge(
                                                                param["status"]
                                                            ),
                                                            class_name="flex justify-between items-center mb-1",
                                                        ),
                                                        rx.el.p(
                                                            param["message"],
                                                            class_name="text-xs text-gray-500",
                                                        ),
                                                        class_name="p-3 bg-gray-50 rounded-lg border border-gray-100",
                                                    ),
                                                ),
                                                class_name="space-y-2",
                                            ),
                                            class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-100",
                                        ),
                                        rx.el.div(
                                            rx.el.h3(
                                                "Infusion Recommendations",
                                                class_name="text-lg font-bold text-gray-900 mb-4",
                                            ),
                                            rx.el.div(
                                                rx.el.div(
                                                    rx.el.div(
                                                        rx.el.p(
                                                            "Science Max",
                                                            class_name="text-xs text-gray-500 uppercase font-bold",
                                                        ),
                                                        rx.el.p(
                                                            (
                                                                PasteStudioState.paste_result[
                                                                    "infusion"
                                                                ]["science_max"]
                                                                * 100
                                                            ).to_string()
                                                            + "%",
                                                            class_name="text-xl font-bold text-gray-900",
                                                        ),
                                                    ),
                                                    rx.el.div(
                                                        rx.el.p(
                                                            "Rec. Max",
                                                            class_name="text-xs text-gray-500 uppercase font-bold",
                                                        ),
                                                        rx.el.p(
                                                            (
                                                                PasteStudioState.paste_result[
                                                                    "infusion"
                                                                ]["recommended_max"]
                                                                * 100
                                                            ).to_string()
                                                            + "%",
                                                            class_name="text-xl font-bold text-green-600",
                                                        ),
                                                    ),
                                                    rx.el.div(
                                                        rx.el.p(
                                                            "Default",
                                                            class_name="text-xs text-gray-500 uppercase font-bold",
                                                        ),
                                                        rx.el.p(
                                                            (
                                                                PasteStudioState.paste_result[
                                                                    "infusion"
                                                                ]["recommended_default"]
                                                                * 100
                                                            ).to_string()
                                                            + "%",
                                                            class_name="text-xl font-bold text-violet-600",
                                                        ),
                                                    ),
                                                    class_name="grid grid-cols-3 gap-4 mb-6 p-4 bg-violet-50 rounded-xl",
                                                ),
                                                rx.el.ul(
                                                    rx.foreach(
                                                        PasteStudioState.paste_result[
                                                            "infusion"
                                                        ]["commentary"],
                                                        lambda item: rx.el.li(
                                                            item,
                                                            class_name="text-sm text-gray-600 mb-2 pl-4 relative before:content-['•'] before:absolute before:left-0 before:text-violet-400",
                                                        ),
                                                    ),
                                                    class_name="space-y-1",
                                                ),
                                            ),
                                            class_name="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 h-fit",
                                        ),
                                        class_name="grid grid-cols-1 lg:grid-cols-2 gap-6",
                                    ),
                                ),
                                class_name="animate-fade-in",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "flask-conical",
                                    class_name="h-16 w-16 text-gray-200 mb-4",
                                ),
                                rx.el.p(
                                    "Select a sweet and design the paste to see results.",
                                    class_name="text-gray-500 text-lg font-medium",
                                ),
                                class_name="flex flex-col items-center justify-center h-full min-h-[400px] bg-white rounded-2xl border-2 border-dashed border-gray-100",
                            ),
                        ),
                        class_name="w-full lg:w-2/3",
                    ),
                    class_name="flex flex-col lg:flex-row gap-8",
                ),
                class_name="container mx-auto px-4 py-8 max-w-7xl",
            ),
            class_name="flex-1 bg-gray-50 min-h-screen",
        ),
        footer(),
        class_name="flex flex-col min-h-screen",
    )


app = rx.App(theme=rx.theme(appearance="light"))
app.add_page(index, route="/", title="Paste Studio - Indian Sweets Formulation")
app.add_page(
    paste_studio, route="/paste-studio", title="Paste Studio - Formulation Engine"
)