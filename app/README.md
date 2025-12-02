# App Architecture

## Directory Structure

- `calculators/`: Core scientific logic (Viscosity, Water Activity, Dosage).
- `components/`: Reusable UI components (Charts, Cards, Forms).
- `constants/`: Scientific constants and configuration.
- `database/`: Database clients and mappers.
- `engines/`: Business logic orchestrators (Classifier, SOP Generator).
- `services/`: High-level services connecting engines and state.
- `states/`: Reflex state management.
- `validators/`: Quality and safety checks.

## Key Flows

1. **Search**: User searches for a recipe -> `GelatoUniversityClient` queries Supabase.
2. **Formulation**: 
   - `IngredientClassifier` maps ingredients to classes (A-F).
   - `SweetToPasteEngine` scales and balances the mix.
   - `PropertyCalculator` derives physical properties.
   - `SOPGenerator` creates the processing steps.
3. **Display**: Results are rendered via `FormulationState`.
