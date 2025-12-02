from app.constants.gelato_science_constants import GelatoConstants


class FormulationValidator:
    """
    Validates the safety and quality of the formulation.
    """

    @staticmethod
    def validate_formulation(data: dict) -> list[dict]:
        """
        Returns a list of validation results (Pass/Warning/Fail).
        """
        results = []
        props = data.get("properties", {})
        comp = data.get("composition", {})
        aw = props.get("water_activity", 1.0)
        if GelatoConstants.AW_MIN_OPTIMAL <= aw <= GelatoConstants.AW_MAX_OPTIMAL:
            results.append(
                {
                    "check": "Water Activity",
                    "status": "PASS",
                    "msg": f"Aw {aw} is optimal.",
                }
            )
        elif aw < GelatoConstants.AW_MIN_OPTIMAL:
            results.append(
                {
                    "check": "Water Activity",
                    "status": "WARNING",
                    "msg": f"Aw {aw} is low. Paste may be hard.",
                }
            )
        else:
            results.append(
                {
                    "check": "Water Activity",
                    "status": "FAIL",
                    "msg": f"Aw {aw} is too high! Risk of spoilage.",
                }
            )
        fat = comp.get("fat", 0)
        if GelatoConstants.FAT_MIN <= fat <= GelatoConstants.FAT_MAX:
            results.append(
                {
                    "check": "Fat Content",
                    "status": "PASS",
                    "msg": f"Fat {fat}% is within range.",
                }
            )
        elif fat > GelatoConstants.FAT_MAX:
            results.append(
                {
                    "check": "Fat Content",
                    "status": "WARNING",
                    "msg": "High fat may cause separation.",
                }
            )
        else:
            results.append(
                {
                    "check": "Fat Content",
                    "status": "PASS",
                    "msg": "Fat content is acceptable.",
                }
            )
        sugar = comp.get("sugar", 0)
        if sugar >= GelatoConstants.SUGAR_MIN:
            results.append(
                {
                    "check": "Sugar Content",
                    "status": "PASS",
                    "msg": "Sugar adequate for preservation.",
                }
            )
        else:
            results.append(
                {
                    "check": "Sugar Content",
                    "status": "FAIL",
                    "msg": "Sugar too low for preservation!",
                }
            )
        return results