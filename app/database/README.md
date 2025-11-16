# Paste Studio - Supabase Database Setup

This document provides instructions for setting up the required PostgreSQL tables in your Supabase project. The schema is defined in `schema.sql`.

## One-Time Setup via Supabase Dashboard

The easiest way to set up your database is to run the SQL script directly in the Supabase SQL Editor.

### Steps:

1.  **Navigate to the SQL Editor**:
    *   Go to your Supabase project dashboard.
    *   In the left-hand navigation pane, click on the **SQL Editor** icon (it looks like a terminal window).

2.  **Create a New Query**:
    *   In the SQL Editor, click on **+ New query**.

3.  **Copy and Paste the Schema**:
    *   Open the `app/database/schema.sql` file in your code editor.
    *   Copy the entire contents of the file.
    *   Paste the copied SQL into the query window in the Supabase SQL Editor.

4.  **Run the Query**:
    *   Click the **RUN** button (or use the `Cmd/Ctrl + Enter` shortcut).

5.  **Verify Creation**:
    *   After the query finishes, you should see a "Success. No rows returned" message.
    *   You can verify that the tables were created by navigating to the **Table Editor** (grid icon in the left pane). You should see `ingredients_master`, `processing_rules`, and `formulation_constants` in your list of tables.

### SQL Commands to Run

For reference, these are the tables and indexes that will be created:

sql
-- Creates the ingredients_master table
CREATE TABLE IF NOT EXISTS ingredients_master (...);

-- Creates the processing_rules table
CREATE TABLE IF NOT EXISTS processing_rules (...);

-- Creates the formulation_constants table
CREATE TABLE IF NOT EXISTS formulation_constants (...);

-- Creates indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_ingredients_master_name ON ingredients_master(name);
CREATE INDEX IF NOT EXISTS idx_ingredients_master_class ON ingredients_master(class);
CREATE INDEX IF NOT EXISTS idx_processing_rules_ingredient_class ON processing_rules(ingredient_class);


## Testing the Connection

Once the tables are created, you can run the application. The `seed_initial_data()` function in `supabase_client.py` will populate the `ingredients_master` table with some default ingredients on the first run.
# Paste Studio - Supabase Database Setup

This document provides instructions for setting up the required PostgreSQL tables in your Supabase project. The schema is defined in `schema.sql`.

## One-Time Setup via Supabase Dashboard

The easiest way to set up your database is to run the SQL script directly in the Supabase SQL Editor.

### Steps:

1.  **Navigate to the SQL Editor**:
    *   Go to your Supabase project dashboard.
    *   In the left-hand navigation pane, click on the **SQL Editor** icon (it looks like a terminal window).

2.  **Create a New Query**:
    *   In the SQL Editor, click on **+ New query**.

3.  **Copy and Paste the Schema**:
    *   Open the `app/database/schema.sql` file in your code editor.
    *   Copy the entire contents of the file.
    *   Paste the copied SQL into the query window in the Supabase SQL Editor.

4.  **Run the Query**:
    *   Click the **RUN** button (or use the `Cmd/Ctrl + Enter` shortcut).

5.  **Verify Creation**:
    *   After the query finishes, you should see a "Success. No rows returned" message.
    *   You can verify that the tables were created by navigating to the **Table Editor** (grid icon in the left pane). You should see `ingredients_master`, `processing_rules`, and `formulation_constants` in your list of tables.

### SQL Commands to Run

For reference, these are the tables and indexes that will be created:

sql
-- Creates the ingredients_master table
CREATE TABLE IF NOT EXISTS ingredients_master (...);

-- Creates the processing_rules table
CREATE TABLE IF NOT EXISTS processing_rules (...);

-- Creates the formulation_constants table
CREATE TABLE IF NOT EXISTS formulation_constants (...);

-- Creates indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_ingredients_master_name ON ingredients_master(name);
CREATE INDEX IF NOT EXISTS idx_ingredients_master_class ON ingredients_master(class);
CREATE INDEX IF NOT EXISTS idx_processing_rules_ingredient_class ON processing_rules(ingredient_class);


## Testing the Connection

Once the tables are created, you can run the application. The `seed_initial_data()` function in `supabase_client.py` will populate the `ingredients_master` table with some default ingredients on the first run.
