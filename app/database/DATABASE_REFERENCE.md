# Database Reference Documentation

## 🗺️ Architecture Overview

The Paste Studio MVP uses a PostgreSQL database hosted on Supabase. The database is designed to support a scientific formulation engine that converts traditional recipes into precision-engineered gelato pastes.

### Core Tables

| Table Name | Purpose | Record Count | Key Modules |
|------------|---------|--------------|-------------|
| `ingredients_master` | Nutritional & physical properties of raw ingredients | 100+ | `IngredientClassifier` |
| `processing_rules` | Logic for generating Standard Operating Procedures (SOPs) | 14+ | `SOPGenerator` |
| `formulation_constants` | Physical constants for scientific calculations (Aw, Viscosity) | 16+ | `PropertyCalculator` |
| `desserts_master_v2` | Legacy database of traditional Indian sweet recipes | 1000+ | `GelatoUniversityClient` |

---

## 📊 Table Schemas

### 1. ingredients_master

**Purpose:** The source of truth for ingredient properties. Used to classify raw recipe inputs into processing classes (A-F) and calculate the nutritional composition of the final paste.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Unique identifier |
| `name` | VARCHAR(100) | Unique ingredient name (e.g., "khoya") |
| `class` | VARCHAR(20) | Processing class (A_DAIRY, B_NUT, etc.) |
| `aliases` | TEXT[] | Common alternative names (e.g., ["mawa", "khoa"]) |
| `moisture_pct` | FLOAT | Water content percentage |
| `fat_pct` | FLOAT | Fat content percentage |
| `protein_pct` | FLOAT | Protein content percentage |
| `sugar_pct` | FLOAT | Sugar content percentage |
| `processing_temp_c` | INT | Ideal processing temperature |
| `processing_time_min` | INT | Standard processing time |
| `equipment_type` | VARCHAR(100) | Required equipment (e.g., "Wet grinder") |
| `created_at` | TIMESTAMP | Record creation timestamp |

**Sample Data:**
sql
INSERT INTO ingredients_master (name, class, moisture_pct, fat_pct, processing_temp_c)
VALUES ('pistachio', 'B_NUT', 4.0, 45.0, 120);


### 2. processing_rules

**Purpose:** Defines the step-by-step logic for processing different ingredient classes. The `SOPGenerator` engine queries this table to build the final production workflow.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Unique identifier |
| `ingredient_class` | VARCHAR(20) | Target class (e.g., "A_DAIRY") |
| `step_order` | INT | Sequence number for the step |
| `action` | VARCHAR(200) | Instruction text (e.g., "Pasteurize mixture") |
| `temperature_c` | INT | Target temperature for this step |
| `time_minutes` | INT | Duration of the step |
| `equipment` | VARCHAR(100) | Required equipment |
| `science_reason` | TEXT | Scientific justification for the step |

**Sample Data:**
sql
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, science_reason)
VALUES ('A_DAIRY', 1, 'Heat milk/dairy base', 85, 'Pasteurization kills pathogens');


### 3. formulation_constants

**Purpose:** Stores physical and chemical constants used in the mathematical models for Water Activity (Norrish Equation) and Viscosity (Power Law).

| Column | Type | Description |
|--------|------|-------------|
| `constant_name` | VARCHAR(100) PK | Unique key (e.g., "K_SUGAR_NORRISH") |
| `value` | FLOAT | Numeric value |
| `unit` | VARCHAR(50) | Unit of measurement |
| `source` | TEXT | Scientific paper or standard source |

**Sample Data:**
sql
INSERT INTO formulation_constants (constant_name, value, unit)
VALUES ('AW_TARGET_MAX', 0.75, 'aw');


### 4. desserts_master_v2 (Legacy)

**Purpose:** A read-only library of traditional recipes used as the starting point for formulations. Note: This schema is flexible as it comes from a legacy source.

| Column | Type | Description |
|--------|------|-------------|
| `RecipeID` | VARCHAR/INT PK | Unique Recipe ID |
| `RecipeName` | VARCHAR | Name of the sweet |
| `Ingredients` | TEXT | Comma-separated list of ingredients |
| `Instructions` | TEXT | Original text instructions |

---

## 🔄 Data Flow Architecture

The application interacts with the database in a specific sequence during the formulation process:

mermaid
sequenceDiagram
    participant User
    participant App as Application
    participant DB as Supabase DB

    User->>App: 1. Search "Gulab Jamun"
    App->>DB: SELECT * FROM desserts_master_v2 WHERE name LIKE '%Gulab%'
    DB-->>App: Returns Recipe JSON

    App->>App: 2. Parse Ingredients
    loop For each ingredient
        App->>DB: SELECT * FROM ingredients_master WHERE name = 'khoya'
        DB-->>App: Returns {class: 'A_DAIRY', moisture: 20%, ...}
    end

    App->>App: 3. Calculate Properties
    App->>DB: SELECT * FROM formulation_constants
    DB-->>App: Returns {K_SUGAR: 6.47, ...}
    App->>App: Run Norrish Equation & Viscosity Model

    App->>App: 4. Generate SOP
    loop For each class present
        App->>DB: SELECT * FROM processing_rules WHERE class = 'A_DAIRY'
        DB-->>App: Returns Steps [1, 2, 3...]
    end

    App->>User: Display Final Formulation


---

## 🔗 Module Mappings

This table maps Python modules in the `app/` directory to the database tables they interact with.

| Python Module | Database Table | Interaction Type |
|---------------|----------------|------------------|
| `app/database/gelato_university_client.py` | `desserts_master_v2` | READ (Search) |
| `app/database/gelato_university_client.py` | `processing_rules` | READ (SOP Gen) |
| `app/database/ingredient_mapper.py` | `ingredients_master` | READ (Classification) |
| `app/engines/ingredient_classifier.py` | `ingredients_master` | READ (Enrichment) |
| `app/engines/sop_generator.py` | `processing_rules` | READ (Steps) |
| `app/calculators/*.py` | `formulation_constants` | READ (Constants) |

---

## 📝 Common Queries

### Search for a Recipe
sql
SELECT "RecipeID", "RecipeName", "Ingredients"
FROM desserts_master_v2
WHERE "RecipeName" ILIKE '%mysore pak%'
LIMIT 5;


### Get Processing Rules for a specific Class
sql
SELECT step_order, action, temperature_c, equipment
FROM processing_rules
WHERE ingredient_class = 'B_NUT'
ORDER BY step_order ASC;


### Check Ingredient Properties
sql
SELECT name, class, moisture_pct, fat_pct
FROM ingredients_master
WHERE 'cashew' = ANY(aliases) OR name = 'cashew';


---

## 🔌 Connection Configuration

Database connection is managed via the Supabase Python client.

**File:** `app/database/supabase_client.py`

**Environment Variables:**
- `SUPABASE_URL`: The REST API URL for your Supabase project.
- `SUPABASE_KEY`: The public `anon` key (or `service_role` key for admin tasks).

**Usage Pattern:**

from app.database.supabase_client import get_supabase

supabase = get_supabase()
response = supabase.table("table_name").select("*").execute()
