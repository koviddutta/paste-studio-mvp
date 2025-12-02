import reflex as rx
from app.states.formulation_state import FormulationState


def custom_legend_item(item: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            class_name="w-3 h-3 rounded-full", style={"backgroundColor": item["fill"]}
        ),
        rx.el.span(item["name"], class_name="text-sm text-gray-600"),
        class_name="flex items-center gap-2",
    )


def distribution_charts() -> rx.Component:
    return rx.cond(
        FormulationState.formulation_result,
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Composition Analysis", class_name="text-lg font-semibold mb-6"
                ),
                rx.el.div(
                    rx.recharts.pie_chart(
                        rx.recharts.pie(
                            data=FormulationState.composition_chart_data,
                            data_key="value",
                            name_key="name",
                            cx="50%",
                            cy="50%",
                            outer_radius=100,
                            fill="#8884d8",
                            label=True,
                            stroke="#fff",
                            stroke_width=2,
                        ),
                        height=300,
                        width="100%",
                    ),
                    rx.el.div(
                        rx.foreach(
                            FormulationState.composition_chart_data, custom_legend_item
                        ),
                        class_name="flex flex-wrap justify-center gap-4 mt-4",
                    ),
                    class_name="flex flex-col justify-center items-center",
                ),
                class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100",
            ),
            rx.el.div(
                rx.el.h3(
                    "Ingredient Breakdown", class_name="text-lg font-semibold mb-6"
                ),
                rx.el.div(
                    rx.recharts.bar_chart(
                        rx.recharts.bar(
                            data_key="batch_weight_g",
                            fill="#8B5CF6",
                            name="Weight (g)",
                            radius=[4, 4, 0, 0],
                        ),
                        rx.recharts.x_axis(
                            data_key="name",
                            interval=0,
                            angle=-45,
                            text_anchor="end",
                            height=80,
                        ),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        data=FormulationState.formulation_result["ingredients"],
                        height=300,
                        width="100%",
                        margin={"bottom": 20},
                    ),
                    class_name="w-full",
                ),
                class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8",
        ),
    )