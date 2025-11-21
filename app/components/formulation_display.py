import reflex as rx
from app.states.formulation_state import FormulationState, RecipeIngredient, SOPStep
from typing import Union


def _property_card(
    icon: str, label: str, value: Union[str, int, float, rx.Var], unit: str, color: str
) -> rx.Component:
    """A card to display a single calculated property."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-6 w-6 {color}"),
            class_name="p-2 bg-gray-100 rounded-lg",
        ),
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(
                value,
                rx.el.span(unit, class_name="text-sm font-medium text-gray-500 ml-1"),
                class_name="text-xl font-bold text-gray-800",
            ),
            class_name="flex flex-col",
        ),
        class_name="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-xl shadow-sm w-full",
    )


def _validation_status_badge(status: rx.Var[str]) -> rx.Component:
    """A badge to display validation status (PASS, WARNING, FAIL)."""
    return rx.el.span(
        status,
        class_name=rx.cond(
            status == "PASS",
            "px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full",
            rx.cond(
                status == "WARNING",
                "px-2 py-1 text-xs font-semibold text-yellow-800 bg-yellow-100 rounded-full",
                "px-2 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full",
            ),
        ),
    )


def _ingredient_row(ingredient: RecipeIngredient) -> rx.Component:
    """A single row in the ingredients table."""
    return rx.el.tr(
        rx.el.td(
            ingredient["name"], class_name="px-4 py-3 text-sm text-gray-800 font-medium"
        ),
        rx.el.td(
            ingredient["mass_g"].to_string(),
            class_name="px-4 py-3 text-sm text-gray-600",
        ),
        rx.el.td(
            rx.cond(
                ingredient["classified_data"],
                ingredient["classified_data"]["class_name"].replace("_", " "),
                rx.el.span("Unclassified", class_name="text-red-500"),
            ),
            class_name="px-4 py-3 text-sm text-gray-600",
        ),
        rx.el.td(
            rx.cond(
                ingredient["classified_data"]
                & (ingredient["classified_data"]["moisture_pct"] != None),
                ingredient["classified_data"]["moisture_pct"].to_string() + "%",
                "N/A",
            ),
            class_name="px-4 py-3 text-sm text-gray-600",
        ),
        rx.el.td(
            rx.cond(
                ingredient["classified_data"]
                & (ingredient["classified_data"]["fat_pct"] != None),
                ingredient["classified_data"]["fat_pct"].to_string() + "%",
                "N/A",
            ),
            class_name="px-4 py-3 text-sm text-gray-600",
        ),
    )


def _sop_step_item(step: SOPStep) -> rx.Component:
    """A single interactive SOP step."""
    return rx.el.div(
        rx.el.div(
            rx.el.input(
                type="checkbox",
                checked=FormulationState.completed_sop_steps.contains(step["step"]),
                on_change=lambda _: FormulationState.toggle_sop_step(step["step"]),
                class_name="h-4 w-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500",
            ),
            rx.el.div(
                rx.el.p(
                    f"Step {step['step']}: {step['title']}",
                    class_name="font-semibold text-gray-800",
                ),
                rx.el.p(step["action"], class_name="text-sm text-gray-600"),
                rx.el.p(
                    step["science_reason"],
                    class_name="text-xs text-gray-500 italic mt-1",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.cond(
                    step["temperature_c"] != None,
                    rx.el.div(
                        rx.icon("thermometer", class_name="h-4 w-4 text-orange-500"),
                        rx.el.span(
                            f"{step['temperature_c']}°C",
                            class_name="text-sm font-medium",
                        ),
                        class_name="flex items-center gap-1",
                    ),
                ),
                rx.cond(
                    step["time_minutes"] != None,
                    rx.el.div(
                        rx.icon("timer", class_name="h-4 w-4 text-blue-500"),
                        rx.el.span(
                            f"{step['time_minutes']} min",
                            class_name="text-sm font-medium",
                        ),
                        class_name="flex items-center gap-1",
                    ),
                ),
                rx.cond(
                    step["equipment"] != None,
                    rx.el.div(
                        rx.icon("blend", class_name="h-4 w-4 text-gray-500"),
                        rx.el.span(step["equipment"], class_name="text-sm font-medium"),
                        class_name="flex items-center gap-1",
                    ),
                ),
                class_name="flex flex-col items-end gap-1 text-gray-600",
            ),
            class_name="flex items-start gap-4",
        ),
        class_name="p-4 border-b border-gray-200",
    )


def formulation_results_display() -> rx.Component:
    """Displays the generated formulation results, warnings, or errors."""
    result = FormulationState.formulation_result
    return rx.el.div(
        rx.cond(
            FormulationState.error_message != "",
            rx.el.div(
                rx.icon("badge_alert", class_name="h-5 w-5 text-red-500"),
                rx.el.p(
                    FormulationState.error_message,
                    class_name="font-medium text-red-700",
                ),
                class_name="flex items-center gap-3 p-4 bg-red-100 border border-red-200 rounded-lg w-full max-w-4xl",
            ),
        ),
        rx.cond(
            result,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            f"Formulation: {result['sweet_name']}",
                            class_name="text-3xl font-bold text-gray-900 tracking-tight",
                        ),
                        rx.el.p(
                            f"Batch Size: {result['batch_size_kg'].to_string()} kg",
                            class_name="text-md text-gray-500",
                        ),
                    ),
                    rx.el.button(
                        rx.icon("download", class_name="h-4 w-4 mr-2"),
                        "Download PDF",
                        on_click=rx.toast("PDF download coming soon!"),
                        class_name="px-4 py-2 text-sm font-semibold text-white bg-purple-600 rounded-lg shadow-sm hover:bg-purple-700 transition-colors",
                    ),
                    class_name="flex items-center justify-between mb-8",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "Standard Operating Procedure (SOP)",
                            class_name="text-xl font-semibold text-gray-800 mb-4",
                        ),
                        rx.el.div(
                            rx.foreach(result["sop"], _sop_step_item),
                            class_name="bg-white border border-gray-200 rounded-xl shadow-sm max-h-[800px] overflow-y-auto",
                        ),
                        class_name="flex flex-col gap-4 col-span-1 lg:col-span-2",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Calculated Properties",
                                class_name="text-xl font-semibold text-gray-800 mb-4",
                            ),
                            rx.el.div(
                                _property_card(
                                    "droplets",
                                    "Water Activity",
                                    result["properties"]["water_activity"].to_string(),
                                    "aw",
                                    "text-blue-500",
                                ),
                                _property_card(
                                    "calendar-days",
                                    "Shelf Life",
                                    result["properties"][
                                        "shelf_life_weeks"
                                    ].to_string(),
                                    "weeks",
                                    "text-green-500",
                                ),
                                _property_card(
                                    "test_tube",
                                    "Viscosity",
                                    result["properties"]["viscosity_pas"].to_string(),
                                    "Pa·s",
                                    "text-yellow-500",
                                ),
                                _property_card(
                                    "ice_cream_cone",
                                    "Dosage",
                                    result["properties"][
                                        "dosage_g_per_kg_base"
                                    ].to_string(),
                                    "g/kg",
                                    "text-pink-500",
                                ),
                                class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                            ),
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Validation Report",
                                class_name="text-xl font-semibold text-gray-800 mb-4",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    result["validation"]["results"],
                                    lambda res: rx.el.div(
                                        _validation_status_badge(res["status"]),
                                        rx.el.p(
                                            res["message"],
                                            class_name="text-sm text-gray-700",
                                        ),
                                        class_name="flex items-center gap-3 p-3 bg-white border-l-4 rounded-r-lg",
                                        border_left_color=rx.cond(
                                            res["status"] == "PASS",
                                            "var(--green-500)",
                                            rx.cond(
                                                res["status"] == "WARNING",
                                                "var(--yellow-500)",
                                                "var(--red-500)",
                                            ),
                                        ),
                                    ),
                                ),
                                class_name="space-y-3",
                            ),
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Ingredients Breakdown",
                                class_name="text-xl font-semibold text-gray-800 mb-4",
                            ),
                            rx.el.div(
                                rx.el.table(
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th(
                                                "Ingredient", class_name="text-left"
                                            ),
                                            rx.el.th(
                                                "Mass (g)", class_name="text-left"
                                            ),
                                            rx.el.th("Class", class_name="text-left"),
                                            rx.el.th(
                                                "Moisture", class_name="text-left"
                                            ),
                                            rx.el.th("Fat", class_name="text-left"),
                                            class_name="bg-gray-50",
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            result["ingredients"], _ingredient_row
                                        )
                                    ),
                                    class_name="w-full table-auto",
                                ),
                                class_name="w-full overflow-hidden border border-gray-200 rounded-xl",
                            ),
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.h3(
                                    "Composition",
                                    class_name="text-lg font-semibold text-gray-800 mb-2",
                                ),
                                rx.foreach(
                                    result["properties"]["composition_pct"].keys(),
                                    lambda key: rx.el.div(
                                        rx.el.p(
                                            key.capitalize().replace("_", " "),
                                            class_name="text-sm text-gray-600 font-medium",
                                        ),
                                        rx.el.p(
                                            result["properties"]["composition_pct"][
                                                key
                                            ].to_string()
                                            + "%",
                                            class_name="text-sm text-gray-800 font-bold",
                                        ),
                                        class_name="flex justify-between",
                                    ),
                                ),
                                class_name="p-4 bg-white border border-gray-200 rounded-xl shadow-sm",
                            ),
                            rx.cond(
                                result["warnings"].length() > 0,
                                rx.el.div(
                                    rx.el.h3(
                                        "Warnings",
                                        class_name="text-lg font-semibold text-yellow-800 mb-2",
                                    ),
                                    rx.el.ul(
                                        rx.foreach(
                                            result["warnings"],
                                            lambda warning: rx.el.li(
                                                rx.icon(
                                                    "flag_triangle_right",
                                                    class_name="h-4 w-4 text-yellow-600 mr-2 shrink-0",
                                                ),
                                                warning,
                                                class_name="flex items-start text-sm text-yellow-700",
                                            ),
                                        ),
                                        class_name="list-none space-y-1",
                                    ),
                                    class_name="p-4 bg-yellow-50 border border-yellow-200 rounded-xl mt-4",
                                ),
                            ),
                            class_name="grid grid-cols-1 gap-4",
                        ),
                        class_name="flex flex-col gap-8 col-span-1",
                    ),
                    class_name="grid grid-cols-1 lg:grid-cols-3 gap-8",
                ),
                class_name="w-full max-w-7xl p-6 bg-gray-50 rounded-2xl mt-8",
            ),
        ),
        class_name="w-full flex flex-col items-center mt-8 px-4",
    )