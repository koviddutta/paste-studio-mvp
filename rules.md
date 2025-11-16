Project Name: Paste Studio MVP – Indian Sweets Paste Formulation Engine
What It Does
– Uses 1000+ Indian sweet recipes from Supabase
– Classifies each ingredient into 6 processing classes (Dairy, Nut, Sugar & Binders, Fat, Stabilizer, Aromatic)
– Generates a detailed step-by-step production SOP (up to ~40 steps)
– Calculates key properties (water activity, estimated shelf-life, viscosity, dosage for gelato base)
– Runs basic safety checks (pasteurisation steps, water activity range, typical sugar/fat limits)
– Outputs a full formulation + downloadable PDF SOP

**Tech Stack**:
- Backend: Python 3.9+ + FastAPI
- Frontend: Reflex (React-based)
- Database: Supabase PostgreSQL
- Storage: Supabase or MinIO
- Deployment: Reflex Cloud

**Timeline**: 4 weeks to MVP

## CODING STANDARDS

### Code Style
- Python: PEP 8 (black formatter)
- Naming: snake_case for functions, UPPER_CASE for constants
- Functions: Max 50 lines, single responsibility
- Type hints: Always add types to function parameters
- Docstrings: Google format for all functions
- Error handling: Try-except with specific error types

### Quality
- DRY principle: No copy-paste code
- Comments: Only for WHY, not WHAT
- Tests: Write as you code (pytest)
- Logging: Use logging module, not print()
- Performance: Consider database query optimization

### Security
- NEVER hardcode secrets (use .env)
- NEVER commit .env files
- Use environment variables for all credentials
- Validate all user input
- Use parameterized queries (SQL injection prevention)

---

## PROJECT STRUCTURE

```
paste-studio-mvp/
├── backend/
│   ├── main.py (FastAPI app entry point)
│   ├── requirements.txt
│   ├── .env (NEVER commit - credentials)
│   ├── .env.example (COMMIT - template)
│   ├── engines/
│   │   ├── ingredient_classifier.py
│   │   ├── sop_generator.py
│   │   └── process_orchestrator.py
│   ├── database/
│   │   ├── supabase_client.py
│   │   ├── schema.sql
│   │   └── migrations.py
│   ├── calculators/
│   │   ├── property_calculator.py
│   │   ├── water_activity.py
│   │   └── viscosity.py
│   ├── validators/
│   │   └── formulation_validator.py
│   └── api/
│       ├── endpoints.py
│       ├── models.py
│       └── schemas.py
│
├── frontend/
│   ├── rxconfig.py (Reflex config)
│   ├── state.py (State management)
│   ├── requirements.txt
│   ├── .env.example
│   ├── pages/
│   │   ├── search.py
│   │   ├── formulation.py
│   │   ├── sop.py
│   │   ├── troubleshoot.py
│   │   └── index.py
│   └── components/
│       ├── header.py
│       ├── footer.py
│       └── recipe_selector.py
│
├── data/
│   ├── ingredients_master.json
│   └── processing_rules.json
│
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

## CORE CONCEPTS

### 6 Ingredient Classes (A-F)

**Class A: Dairy** (Khoya, Milk, Paneer, Cream)
- moisture: 20-50%, fat: 20-35%, protein: 10-20%
- processing: Pasteurize 85°C/30s
- equipment: Blender

**Class B: Nuts** (Pistachio, Almond, Cashew, Walnut)
- moisture: <5%, fat: 40-65%, protein: 15-25%
- processing: Roast 120°C/10min, grind <40μm
- equipment: Wet grinder

**Class C: Sugars** (Sucrose, Jaggery, Glucose)
- moisture: 0-5%, fat: 0%, protein: 0%
- processing: Dissolve 60-70°C
- equipment: Pot

**Class D: Fats** (Ghee, Oil, Butter, Cocoa Butter)
- moisture: 0%, fat: 100%, protein: 0%
- processing: Melt 40-50°C, emulsify 65°C
- equipment: Mixer

**Class E: Stabilizers** (LBG, Guar, Lambda, Xanthan)
- moisture: 0%, fat: 0%, protein: 0%
- processing: Sequence hydration 85→65→40°C
- equipment: High-shear mixer

**Class F: Aromatics** (Cardamom, Saffron, Rose Water, Vanilla)
- moisture: 0-95%, fat: 0%, protein: 0%
- processing: Add LAST at <50°C
- equipment: Grinder

---

### Universal 10-Step Algorithm

1. Prepare solids (crumble, wash) - 5 min, 25°C
2. Create aqueous phase (heat water) - 5 min, 60°C
3. Dissolve sugars (no grains visible) - 5 min, 60°C
4. Pasteurize dairy (if dairy base) - 2 min, 85°C, 30s hold
5. Add main solids (dairy/nuts) - 3 min, 85°C
6. Emulsify fats (slow add, high-shear) - 1.5 min, 65°C
7. Hydrate LBG (high-shear) - 5 min, 85°C
8. Hydrate Lambda (cool & mix) - 3 min, 65°C
9. Hydrate Guar (slow, passive) - 60 min, 40°C
10. Cool & add aromatics (gentle mix) - 21 min, 25°C

**Total: ~2 hours, 40-step detailed SOP**

---

### Water Activity (Aw) - Master Number

**Formula**: Norrish equation
```
a_w = X_water × exp(-(K_sugar × X_sugar² + K_protein × X_protein²))
K_sugar = 6.47, K_protein = 4.2
```

**Target**: 0.68-0.75 (12 weeks shelf-life)
**Too low** (<0.60): Rancidity risk
**Too high** (>0.85): Mold growth

**Impact**:
- 0.68-0.75: ✅ Safe (12 weeks room temp)
- 0.75-0.85: ⚠️ Risky (mold slow growth)
- >0.85: ❌ Unsafe (mold fast)

---

## DATABASE SCHEMA

### Table: ingredients_master

```sql
CREATE TABLE ingredients_master (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  class VARCHAR(20) NOT NULL,  -- A_DAIRY, B_NUT, C_SUGAR, D_FAT, E_STABILIZER, F_AROMATIC
  aliases TEXT[] DEFAULT ARRAY[]::TEXT[],
  moisture_pct FLOAT,
  fat_pct FLOAT,
  protein_pct FLOAT,
  sugar_pct FLOAT,
  processing_temp_c INT,
  processing_time_min INT,
  equipment_type VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Table: processing_rules

```sql
CREATE TABLE processing_rules (
  id SERIAL PRIMARY KEY,
  ingredient_class VARCHAR(20) NOT NULL,
  step_order INT NOT NULL,
  action VARCHAR(100),
  temperature_c INT,
  time_minutes INT,
  equipment VARCHAR(100),
  science_reason TEXT
);
```

### Table: formulation_constants

```sql
CREATE TABLE formulation_constants (
  constant_name VARCHAR(100) PRIMARY KEY,
  value FLOAT NOT NULL,
  unit VARCHAR(50),
  source TEXT
);
```

---

## API ENDPOINTS

### POST /api/formulation/generate

```
Request:
{
  "sweet_name": "Gulab Jamun",
  "batch_size_kg": 1.0
}

Response:
{
  "sweet_name": "Gulab Jamun",
  "batch_size_kg": 1.0,
  "ingredients": {
    "khoya": 400,
    "sugar": 300,
    "ghee": 100
  },
  "classified_ingredients": {
    "khoya": "A_DAIRY",
    "sugar": "C_SUGAR",
    "ghee": "D_FAT"
  },
  "sop": [
    {
      "step": 1,
      "title": "Prepare Solids",
      "instructions": "Crumble khoya",
      "temperature_c": 25,
      "time_minutes": 5
    },
    ...40 steps total
  ],
  "properties": {
    "water_activity": 0.72,
    "shelf_life_weeks": 12,
    "viscosity_pas": 10.5,
    "dosage_g_per_kg_base": 90
  },
  "validation": "PASS"
}
```

### GET /api/recipes/search?query=gulab

```
Response:
{
  "results": [
    {"id": 1, "name": "Gulab Jamun"},
    {"id": 2, "name": "Gulab Halwa"}
  ]
}
```

---

## ENVIRONMENT VARIABLES

### Backend .env

```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY
DATABASE_URL=postgresql://pastastudio:password@localhost:5432/paste_studio_db

ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
FRONTEND_URL=http://localhost:3000

MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=secure_password
MINIO_BUCKET=paste-studio

GEMINI_API_KEY=YOUR_GEMINI_KEY (v2 only)
```

### Frontend .env

```
REFLEX_VAR_API_URL=http://localhost:8000
REFLEX_ENV=dev
```

---

## BACKEND IMPLEMENTATION

### Priority 1: Database Connection

```python
# backend/database/supabase_client.py
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

def fetch_recipe(sweet_name: str) -> dict:
    response = supabase.table('recipes').select('*').ilike('name', f'%{sweet_name}%').execute()
    return response.data[0] if response.data else None
```

### Priority 2: Ingredient Classifier

```python
# backend/engines/ingredient_classifier.py
def classify_ingredient(ingredient_name: str) -> str:
    """Classify ingredient into A-F classes"""
    # Query ingredients_master table
    # Handle aliases (mawa → khoya)
    # Return class or "UNKNOWN"
    pass
```

### Priority 3: SOP Generator

```python
# backend/engines/sop_generator.py
def generate_sop(ingredients: dict, batch_size_kg: float) -> list:
    """Generate 40-step SOP from ingredients"""
    # Classify each ingredient
    # Query processing_rules table
    # Create step-by-step sequence
    # Format with temps, times, equipment
    # Return list of 40 steps
    pass
```

### Priority 4: Properties Calculator

```python
# backend/calculators/property_calculator.py
def calculate_water_activity(composition: dict) -> float:
    """Norrish equation for water activity"""
    # Calculate using Norrish constants
    # Return Aw between 0-1
    pass

def calculate_viscosity(composition: dict) -> float:
    """Power law model for viscosity"""
    # Calculate from composition
    # Return Pa·s
    pass
```

### Priority 5: API Endpoints

```python
# backend/api/endpoints.py
@app.post("/api/formulation/generate")
def generate_formulation(sweet_name: str, batch_size_kg: float = 1.0):
    """Main endpoint: Recipe → Complete formulation"""
    # Fetch recipe from Supabase
    # Parse ingredients
    # Classify
    # Generate SOP
    # Calculate properties
    # Validate
    # Return JSON
    pass
```

---

## FRONTEND IMPLEMENTATION

### Priority 1: Page 1 - Search

```python
# frontend/pages/search.py
def search_page():
    """Search bar with autocomplete from 1000+ recipes"""
    # Input field (on_change triggers search)
    # Autocomplete results (call backend API)
    # Batch size input
    # Generate button (calls backend)
    pass
```

### Priority 2: Page 2 - Formulation Display

```python
# frontend/pages/formulation.py
def formulation_page():
    """Display formulation from backend"""
    # Ingredients table
    # Properties (Aw, shelf-life, viscosity)
    # Equipment list
    # Navigation buttons
    pass
```

### Priority 3: Page 3 - SOP Viewer

```python
# frontend/pages/sop.py
def sop_page():
    """Display 40-step SOP"""
    # Step-by-step with temps/times
    # Interactive checkboxes
    # Print/Download buttons
    pass
```

### Priority 4: Page 4 - Troubleshooting

```python
# frontend/pages/troubleshoot.py
def troubleshoot_page():
    """Troubleshooting selector"""
    # Problem dropdown
    # Call backend for solutions
    # Display fixes
    pass
```

---

## CRITICAL RULES

### Temperature Rules (NON-NEGOTIABLE)

✅ DO:
- Heat to 85°C for LBG hydration
- Cool to 65°C before adding fat
- Add aromatics last at <50°C
- Pasteurize dairy 85°C/30s

❌ DON'T:
- Add LBG at 40°C (won't hydrate)
- Add fat at 85°C (emulsion breaks)
- Add cardamom at 85°C (loses aroma)
- Skip pasteurization (safety)

### Validation Gates (MUST PASS)

✅ Water Activity: 0.68-0.75
✅ pH: 5.4-6.8 (if dairy)
✅ Sugar %: 20-40%
✅ Fat %: 10-20%
✅ Stabilizer %: 0.25-0.50%

❌ If any fails: Flag and explain

---

## INTEGRATION REQUIREMENTS

### Supabase (Already Configured)

- Database: PostgreSQL
- 1000+ recipes table (pre-loaded)
- Need to create: ingredients_master, processing_rules, formulation_constants
- Connection: Via Supabase Python SDK

### GitHub (Version Control)

- Repo: paste-studio-mvp
- Never commit: .env, __pycache__, venv/
- Always commit: .env.example, code, docs

### Deployment (Week 4)

- Reflex Cloud (recommended)
- Railway (alternative)
- Environment variables in deployment platform

---

## WHAT AI SHOULD KNOW

### Do This:
- Follow project structure exactly
- Use .env for all credentials
- Type hints on all functions
- Docstrings for all functions
- Error handling with try-except
- Query Supabase efficiently (use indexes)
- Validate all user input
- Test before suggesting

### Don't Do This:
- Hardcode any credentials
- Copy-paste repeated code
- Use print() instead of logging
- Skip error handling
- Write functions >50 lines
- Mix business logic with UI
- Commit .env or secrets
- Assume Supabase connection always works

---

## SUCCESS METRICS FOR CODE

✅ All endpoints tested
✅ No unhandled exceptions
✅ All functions have docstrings
✅ Type hints on all parameters
✅ Follows PEP 8 (black formatted)
✅ No hardcoded values
✅ Proper error messages
✅ Logging instead of print()

---

## IF CODE BREAKS

**"API Key not found"**
→ Check .env exists and is loaded
→ Restart terminal (env reloads)

**"Supabase connection refused"**
→ Check SUPABASE_URL and KEY are correct
→ Test connection: `python -c "from supabase import..."`

**"Reflex won't start"**
→ Clear cache: `rm -rf .web`
→ Update Reflex: `pip install --upgrade reflex`

---

## END MASTER PROMPT

---

## HOW TO USE THIS IN DIFFERENT TOOLS

### **Build.Reflex.dev - Knowledge Base**

```
1. Copy [entire content above]
2. Paste into: Settings → Knowledge Base → Add
3. Save
4. Start coding → AI uses this context automatically

Question to AI: "Generate the database connection file"
AI response: Will follow your architecture, use Supabase, handle errors properly
```

### **Lovable.ai - System Prompt**

```
1. Copy [entire content above]
2. Create new project
3. System Prompt (top right) → Clear → Paste
4. Save
5. Ask: "Build complete backend with Supabase integration"
AI generates: Full FastAPI app, all endpoints, error handling

Result: Working backend that follows your specs
```

### **GitHub Copilot - .copilot-prompt.md**

```
1. Create file in project root: .copilot-prompt.md
2. Paste [entire content above]
3. In VS Code settings:
   github.copilot.enable > true
4. Start typing code → Copilot suggests based on your context

Example:
You type: "def calculate"
Copilot suggests: "def calculate_water_activity(composition: dict) -> float:"
Following your specs exactly
```

### **Claude.ai / ChatGPT**

```
1. Start new conversation
2. Paste [entire content above]
3. Wait for: "I've understood your project..."
4. Then ask: "Generate backend/main.py"
5. AI generates code following all your requirements

Result: Professional-grade code that matches your architecture
```

---

## FINAL CHECKLIST

### Before Using Master Prompt

```
□ All 12 files downloaded (358-381)
□ [382] Master Prompt ready
□ Supabase account created
□ Supabase credentials in .env
□ GitHub repo created
□ .gitignore setup (never commit secrets)
□ Project structure created
□ Python 3.9+ installed
□ Virtual environment created
```

### When Using in AI Tools

```
□ Paste complete master prompt into Knowledge Base
□ Acknowledge receipt ("I understand...")
□ Start asking for code generation
□ Review generated code
□ Adjust .env variables
□ Test locally
□ Push to GitHub
```

---

## SUMMARY: YES, This One File Applies to ALL

**Answer to your question:**

> "Can we just post this file in the prompt and will it apply to all integrations?"

### **YES ✅**

| Integration | Applies? | How |
|---|---|---|
| Supabase | ✅ YES | File specifies SQL schema, connection code |
| GitHub | ✅ YES | File specifies project structure, .gitignore |
| FastAPI | ✅ YES | File specifies endpoints, models, database |
| Reflex | ✅ YES | File specifies pages, state, UI patterns |
| Environment | ✅ YES | File specifies all .env variables |
| Deployment | ✅ YES | File references Reflex Cloud setup |
| Gemini | ✅ YES | File notes it's v2 only (skip MVP) |

**One file → All integrations → Consistent implementation**