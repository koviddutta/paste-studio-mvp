# Indian Sweets Formulation Engine - Supabase Database Setup

This document provides instructions for setting up the required PostgreSQL tables in your Supabase project. The schema is defined in `app/database/schema.sql`.

## One-Time Setup via Supabase Dashboard

The easiest way to set up your database is to run the SQL script directly in the Supabase SQL Editor. This will create all necessary tables and seed them with initial data.

### Steps:

1.  **Navigate to the SQL Editor**:
    *   Go to your Supabase project dashboard.
    *   In the left-hand navigation pane, click on the **SQL Editor** icon.

2.  **Create a New Query**:
    *   In the SQL Editor, click on **+ New query**.

3.  **Copy and Paste the Schema**:
    *   Open the `app/database/schema.sql` file from your project.
    *   Copy the **entire contents** of the file.
    *   Paste the copied SQL into the query window in the Supabase SQL Editor.

4.  **Run the Query**:
    *   Click the **RUN** button (or use the `Cmd/Ctrl + Enter` shortcut).

5.  **Verify Creation**:
    *   After the query finishes, you should see a "Success" message.
    *   Verify that the tables were created by navigating to the **Table Editor** (grid icon in the left pane). You should see the following tables:
        *   `ingredients_master`
        *   `processing_rules`
        *   `formulation_constants`
    *   The `processing_rules` and `formulation_constants` tables will be pre-filled with data.
    *   The `desserts_master_v2` table is assumed to be pre-loaded separately with the 1040+ recipes.

### SQL Commands Summary

The `schema.sql` script will execute the following main actions:

sql
-- Creates the ingredients_master table for classifying ingredients
CREATE TABLE IF NOT EXISTS ingredients_master (...);

-- Creates the processing_rules table for SOP generation
CREATE TABLE IF NOT EXISTS processing_rules (...);

-- Creates the formulation_constants table for property calculations
CREATE TABLE IF NOT EXISTS formulation_constants (...);

-- Seeds the processing_rules table with universal SOP steps
INSERT INTO processing_rules (...) VALUES (...);

-- Seeds the formulation_constants table with scientific values
INSERT INTO formulation_constants (...) VALUES (...);

-- Creates indexes for faster database lookups
CREATE INDEX IF NOT EXISTS idx_ingredients_master_name ON ingredients_master(name);
CREATE INDEX IF NOT EXISTS idx_ingredients_master_class ON ingredients_master(class);
CREATE INDEX IF NOT EXISTS idx_processing_rules_ingredient_class ON processing_rules(ingredient_class);


## Next Steps

Once the database schema is in place, the application will be able to connect to Supabase and perform its core functions:

1.  **Fetch Recipes**: From the `desserts_master_v2` table.
2.  **Classify Ingredients**: Using the `ingredients_master` table.
3.  **Generate SOPs**: By referencing the `processing_rules` table.
4.  **Calculate Properties**: Using values from the `formulation_constants` table.
