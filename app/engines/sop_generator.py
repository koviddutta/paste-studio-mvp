from app.database.gelato_university_client import GelatoUniversityClient


class SOPGenerator:
    """
    Generates Standard Operating Procedures based on ingredient classes.
    """

    @staticmethod
    async def generate_sop(classified_ingredients: list[dict]) -> list[dict]:
        """
        Creates a step-by-step SOP.
        """
        steps = []
        step_counter = 1
        groups = {"A": [], "B": [], "C": [], "D": [], "E": [], "F": []}
        for ing in classified_ingredients:
            raw_class = ing.get("processing_class", "F")
            p_class = raw_class.split("_")[0] if raw_class else "F"
            if p_class in groups:
                groups[p_class].append(ing["name"])
            else:
                groups["F"].append(ing["name"])
        steps.append(
            {
                "step": step_counter,
                "phase": "Preparation",
                "action": "Weigh all ingredients precisely.",
                "details": "Ensure all raw materials are ready.",
                "temp": "20-25°C",
            }
        )
        step_counter += 1
        if groups["B"]:
            rule = await GelatoUniversityClient.get_processing_rules("B")
            steps.append(
                {
                    "step": step_counter,
                    "phase": "Nut Processing",
                    "action": f"Roast {', '.join(groups['B'])}.",
                    "details": f"Roast at {rule.get('min_temp')}-{rule.get('max_temp')}°C to develop flavor.",
                    "temp": f"{rule.get('max_temp')}°C",
                }
            )
            step_counter += 1
            steps.append(
                {
                    "step": step_counter,
                    "phase": "Nut Processing",
                    "action": "Grind to fine paste.",
                    "details": "Particle size should be < 20 microns.",
                    "temp": "40-50°C",
                }
            )
            step_counter += 1
        base_ings = groups["A"] + groups["C"] + groups["D"]
        if base_ings:
            steps.append(
                {
                    "step": step_counter,
                    "phase": "Base Formulation",
                    "action": "Combine wet ingredients and sugars.",
                    "details": f"Mix {', '.join(base_ings)} in the kettle.",
                    "temp": "25°C",
                }
            )
            step_counter += 1
            steps.append(
                {
                    "step": step_counter,
                    "phase": "Heating",
                    "action": "Heat mixture to dissolve solids.",
                    "details": "Agitate continuously.",
                    "temp": "65°C",
                }
            )
            step_counter += 1
        if groups["E"]:
            steps.append(
                {
                    "step": step_counter,
                    "phase": "Stabilization",
                    "action": f"Add {', '.join(groups['E'])} mixed with some sugar.",
                    "details": "Ensure lump-free dispersion.",
                    "temp": "65°C",
                }
            )
            step_counter += 1
        steps.append(
            {
                "step": step_counter,
                "phase": "Pasteurization",
                "action": "Heat to pasteurization temperature.",
                "details": "Hold for 15 seconds to ensure safety.",
                "temp": "85°C",
            }
        )
        step_counter += 1
        if groups["F"]:
            steps.append(
                {
                    "step": step_counter,
                    "phase": "Flavoring",
                    "action": f"Cool down and add {', '.join(groups['F'])}.",
                    "details": "Add volatile aromatics at lower temperature to prevent loss.",
                    "temp": "<45°C",
                }
            )
            step_counter += 1
        steps.append(
            {
                "step": step_counter,
                "phase": "Packaging",
                "action": "Fill into sterilized jars.",
                "details": "Hot fill if possible, or rapid cool then fill.",
                "temp": "40°C",
            }
        )
        return steps