import reflex as rx
from typing import Optional
import logging
from app.api.paste_api import design_paste_and_infusion
from app.database.supabase_client import get_supabase


class PasteStudioState(rx.State):
    """
    State management for the Paste Studio Formulation Engine.
    Handles sweet search, selection, parameter configuration, and engine execution.
    """

    search_query: str = ""
    search_results: list[dict[str, str | int | None]] = []
    is_searching: bool = False
    selected_sweet: Optional[dict[str, str | int | None]] = None
    selected_base: str = "white"
    batch_weight: float = 1000.0
    is_loading: bool = False
    error_message: Optional[str] = None
    paste_result: Optional[dict] = None

    @rx.event
    async def search_sweets(self, query: str):
        """
        Searches for sweets in the sweet_compositions table by name.
        """
        self.search_query = query
        if not query or len(query) < 2:
            self.search_results = []
            return
        self.is_searching = True
        yield
        try:
            supabase = get_supabase()
            response = (
                supabase.table("sweet_compositions")
                .select("id, sweet_name, category")
                .ilike("sweet_name", f"%{query}%")
                .limit(10)
                .execute()
            )
            self.search_results = response.data or []
        except Exception as e:
            logging.exception(f"Error searching sweets: {e}")
            self.error_message = (
                "Failed to search for sweets. Please check database connection."
            )
            self.search_results = []
        finally:
            self.is_searching = False

    @rx.event
    def select_sweet(self, sweet: dict[str, str | int | None]):
        """
        Selects a sweet from the search results.
        """
        self.selected_sweet = sweet
        self.search_query = str(sweet.get("sweet_name", ""))
        self.search_results = []
        self.paste_result = None
        self.error_message = None

    @rx.event
    def set_base(self, base_name: str):
        """
        Sets the gelato base profile (white, kulfi, chocolate).
        """
        self.selected_base = base_name

    @rx.event
    def set_batch_weight(self, weight: float):
        """
        Sets the target batch weight in grams.
        """
        self.batch_weight = float(weight)

    @rx.event
    async def run_paste_engine(self):
        """
        Executes the paste design engine using the selected parameters.
        Calls the synchronous API function design_paste_and_infusion.
        """
        if not self.selected_sweet:
            self.error_message = "Please select a sweet recipe first."
            return
        self.is_loading = True
        self.error_message = None
        self.paste_result = None
        yield
        try:
            sweet_id = int(self.selected_sweet["id"])
            result = design_paste_and_infusion(
                sweet_id=sweet_id,
                base_name=self.selected_base,
                batch_weight_g=self.batch_weight,
            )
            self.paste_result = result
        except ValueError as ve:
            self.error_message = f"Validation Error: {str(ve)}"
            logging.exception(f"Paste engine validation error: {ve}")
        except Exception as e:
            self.error_message = f"Engine Execution Failed: {str(e)}"
            logging.exception(f"Critical error in paste engine: {e}")
        finally:
            self.is_loading = False