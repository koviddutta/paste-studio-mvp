import reflex as rx
from app.states.formulation_state import FormulationState
from app.components.ingredient_distribution import distribution_charts


def property_card(
    label: str, value: str, subtext: str, icon: str, color: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-5 w-5 {color}"),
            rx.el.span(label, class_name="text-sm font-medium text-gray-500"),
            class_name="flex items-center gap-2 mb-2",
        ),
        rx.el.div(value, class_name="text-2xl font-bold text-gray-900"),
        rx.el.div(subtext, class_name="text-xs text-gray-400 mt-1"),
        class_name="bg-white p-4 rounded-xl border border-gray-100 shadow-sm",
    )


def status_badge(status: str) -> rx.Component:
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
                class_name="bg-yellow-100 text-yellow-700 text-xs font-bold px-2 py-1 rounded-full",
            ),
            rx.el.span(
                "FAIL",
                class_name="bg-red-100 text-red-700 text-xs font-bold px-2 py-1 rounded-full",
            ),
        ),
    )


def sop_step(step: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                step["step"],
                class_name="flex items-center justify-center w-8 h-8 rounded-full bg-violet-100 text-violet-600 font-bold text-sm shrink-0",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h4(step["phase"], class_name="font-semibold text-gray-900"),
                    rx.el.p(step["action"], class_name="text-gray-700 mt-1"),
                    rx.el.p(
                        step["details"], class_name="text-sm text-gray-500 mt-1 italic"
                    ),
                    class_name="flex-1",
                ),
                rx.el.div(
                    rx.icon("thermometer", class_name="h-4 w-4 text-orange-500 mr-1"),
                    rx.el.span(
                        step["temp"], class_name="text-sm font-medium text-orange-600"
                    ),
                    class_name="flex items-center bg-orange-50 px-3 py-1 rounded-lg shrink-0 h-fit",
                ),
                class_name="flex gap-4 items-start w-full",
            ),
            class_name="flex gap-4",
        ),
        class_name="p-4 border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors",
    )


def formulation_display() -> rx.Component:
    return rx.cond(
        FormulationState.formulation_result,
        rx.el.div(
            rx.el.div(
                property_card(
                    "Water Activity",
                    FormulationState.formulation_result["properties"][
                        "water_activity"
                    ].to_string(),
                    "Optimal: 0.68-0.75",
                    "droplets",
                    "text-blue-500",
                ),
                property_card(
                    "Shelf Life",
                    FormulationState.formulation_result["properties"][
                        "shelf_life_weeks"
                    ].to_string()
                    + " Weeks",
                    "At 20°C storage",
                    "calendar",
                    "text-green-500",
                ),
                property_card(
                    "Viscosity",
                    FormulationState.formulation_result["properties"][
                        "viscosity_pa_s"
                    ].to_string()
                    + " Pa·s",
                    "Flow consistency",
                    "activity",
                    "text-purple-500",
                ),
                property_card(
                    "Gelato Dosage",
                    FormulationState.formulation_result["properties"][
                        "dosage_g_kg"
                    ].to_string()
                    + " g/kg",
                    "Recommended usage",
                    "scale",
                    "text-orange-500",
                ),
                class_name="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8",
            ),
            distribution_charts(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "Validation Checks", class_name="text-lg font-semibold mb-4"
                        ),
                        rx.el.div(
                            rx.foreach(
                                FormulationState.validation_results,
                                lambda res: rx.el.div(
                                    rx.el.span(
                                        res["check"],
                                        class_name="text-sm font-medium text-gray-700",
                                    ),
                                    rx.el.div(
                                        rx.el.span(
                                            res["msg"],
                                            class_name="text-xs text-gray-500 mr-2",
                                        ),
                                        status_badge(res["status"]),
                                        class_name="flex items-center",
                                    ),
                                    class_name="flex justify-between items-center p-3 bg-gray-50 rounded-lg",
                                ),
                            ),
                            class_name="space-y-2 mb-8",
                        ),
                        class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100",
                    ),
                    rx.el.div(
                        rx.el.h3(
                            "Composition", class_name="text-lg font-semibold mb-4"
                        ),
                        rx.el.table(
                            rx.el.thead(
                                rx.el.tr(
                                    rx.el.th(
                                        "Component",
                                        class_name="text-left py-2 text-xs uppercase text-gray-500",
                                    ),
                                    rx.el.th(
                                        "%",
                                        class_name="text-right py-2 text-xs uppercase text-gray-500",
                                    ),
                                )
                            ),
                            rx.el.tbody(
                                rx.el.tr(
                                    rx.el.td("Total Sugar"),
                                    rx.el.td(
                                        FormulationState.formulation_result[
                                            "composition"
                                        ]["sugar"].to_string()
                                        + "%"
                                    ),
                                ),
                                rx.el.tr(
                                    rx.el.td("Total Fat"),
                                    rx.el.td(
                                        FormulationState.formulation_result[
                                            "composition"
                                        ]["fat"].to_string()
                                        + "%"
                                    ),
                                ),
                                rx.el.tr(
                                    rx.el.td("Moisture"),
                                    rx.el.td(
                                        FormulationState.formulation_result[
                                            "composition"
                                        ]["moisture"].to_string()
                                        + "%"
                                    ),
                                ),
                                rx.el.tr(
                                    rx.el.td("Protein"),
                                    rx.el.td(
                                        FormulationState.formulation_result[
                                            "composition"
                                        ]["protein"].to_string()
                                        + "%"
                                    ),
                                ),
                                class_name="text-sm text-gray-700",
                            ),
                            class_name="w-full",
                        ),
                        class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mt-4",
                    ),
                    class_name="space-y-4",
                ),
                rx.el.div(
                    rx.el.h3("Processing SOP", class_name="text-lg font-semibold mb-4"),
                    rx.el.div(
                        rx.foreach(
                            FormulationState.formulation_result["sop"], sop_step
                        ),
                        class_name="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden",
                    ),
                    class_name="md:col-span-2",
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-8",
            ),
            class_name="animate-fade-in",
        ),
        rx.el.div(
            rx.icon("chef-hat", class_name="h-16 w-16 text-gray-200 mb-4"),
            rx.el.p(
                "Search for a sweet recipe to generate a scientific gelato paste formulation.",
                class_name="text-gray-500 text-center max-w-md",
            ),
            class_name="flex flex-col items-center justify-center py-20 border-2 border-dashed border-gray-100 rounded-xl",
        ),
    )