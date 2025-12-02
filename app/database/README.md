# Database Documentation

## Tables

- **ingredients_master**: The source of truth for nutritional and physical properties of ingredients.
- **desserts_master_v2**: Legacy database of traditional recipes.
- **processing_rules**: SOP configuration for different ingredient classes.

## Connection

Uses Supabase via `supabase-py` client.
Credentials are managed via environment variables.
