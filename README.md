# 🍬 Paste Studio MVP - Indian Sweets Formulation Engine

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Supabase](https://img.shields.io/badge/Database-Supabase-green)](https://supabase.com)

> Production-ready formulation system for converting 1000+ Indian sweet recipes into gelato pastes with scientific precision.

## 🎯 Features

✅ **1000+ Recipe Database** - Traditional Indian sweet recipes from Supabase  
✅ **Smart Ingredient Classification** - 6 processing classes (Dairy, Nut, Sugar, Fat, Stabilizer, Aromatic)  
✅ **Detailed SOPs** - Up to 40-step production procedures with temperatures, times, and equipment  
✅ **Scientific Calculations** - Water activity, shelf-life, viscosity, gelato dosage  
✅ **Safety Validations** - Automated checks for pasteurization, water activity, and composition  
✅ **Interactive UI** - Modern Reflex interface with real-time search and formulation generation  

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Supabase account (free tier works)
- Git

### Installation

1. **Clone the repository:**
bash
git clone https://github.com/koviddutta/paste-studio-mvp.git
cd paste-studio-mvp


2. **Install dependencies:**
bash
pip install -r requirements.txt


3. **Set up environment variables:**
bash
cp .env.example .env


Edit `.env` with your Supabase credentials:
env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY


4. **Set up the database:**

- Go to your [Supabase Dashboard](https://app.supabase.com)
- Navigate to **SQL Editor**
- Copy the contents of `app/database/schema.sql`
- Paste and run the SQL
- Verify tables were created in **Table Editor**

5. **Run the application:**
bash
reflex run


6. **Open in browser:**

http://localhost:3000


## 📁 Project Structure


paste-studio-mvp/
├── app/
│   ├── app.py                    # Main Reflex app
│   ├── calculators/              # Property calculations
│   │   ├── property_calculator.py
│   │   ├── water_activity.py
│   │   └── viscosity.py
│   ├── components/               # UI components
│   │   ├── header.py
│   │   ├── recipe_search.py
│   │   └── formulation_display.py
│   ├── database/                 # Database layer
│   │   ├── supabase_client.py
│   │   └── schema.sql            # ⭐ Run this in Supabase
│   ├── engines/                  # Core logic
│   │   ├── ingredient_classifier.py
│   │   └── sop_generator.py
│   ├── services/                 # Business logic
│   │   └── sweet_to_paste_engine.py
│   ├── states/                   # Reflex state management
│   │   └── formulation_state.py
│   └── validators/               # Safety checks
│       └── formulation_validator.py
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── rxconfig.py                   # Reflex configuration
└── README.md                     # This file


## 🔬 How It Works

### 1. Recipe Search
- User searches from 1000+ Indian sweets
- Autocomplete displays matching recipes
- Select recipe and set batch size

### 2. Ingredient Classification
Each ingredient is classified into one of 6 processing classes:

| Class | Type | Examples | Processing |
|-------|------|----------|------------|
| A | Dairy | Khoya, Milk, Paneer | Pasteurize at 85°C |
| B | Nuts | Pistachio, Almond | Roast at 120°C, grind <40μm |
| C | Sugar | Sucrose, Jaggery | Dissolve at 60-70°C |
| D | Fat | Ghee, Butter | Emulsify at 65°C |
| E | Stabilizer | LBG, Guar | Sequence hydration 85→40°C |
| F | Aromatic | Cardamom, Saffron | Add last at <50°C |

### 3. SOP Generation
- Fetches processing rules for each ingredient class
- Sequences steps based on temperatures and dependencies
- Generates detailed 40-step production procedure
- Includes temps, times, equipment, and scientific reasoning

### 4. Property Calculations

**Water Activity (Aw)** - Norrish Equation:

a_w = X_water × exp(-(K_sugar × X_sugar² + K_protein × X_protein²))
K_sugar = 6.47, K_protein = 4.2


**Shelf Life Estimation:**
- 0.68-0.75 Aw: 12 weeks (optimal)
- <0.68: 16 weeks (rancidity risk)
- 0.75-0.85: 4 weeks (slow mold)
- >0.85: 1 week (unsafe)

**Viscosity** - Power Law + Arrhenius:

η = K × γ^(n-1) × exp(Ea/RT)


**Gelato Dosage:**

dosage (g/kg) = 3500 / sugar_concentration_pct


### 5. Safety Validations
- ✅ Water activity: 0.68-0.75
- ✅ Sugar content: 20-40%
- ✅ Fat content: 10-20%
- ✅ Stabilizer: 0.25-0.50%
- ✅ Pasteurization check for dairy

## 🗄️ Database Schema

### Tables Created by `schema.sql`:

1. **ingredients_master** - Ingredient properties and classifications
2. **processing_rules** - Step-by-step processing instructions
3. **formulation_constants** - Scientific constants for calculations
4. **desserts_master_v2** - 1000+ Indian sweet recipes (pre-loaded)

## 🎨 UI Screenshots

### Recipe Search
![Search Interface](assets/placeholder.svg)

### Formulation Results
- Interactive SOP with checkboxes
- Property cards (Aw, shelf-life, viscosity, dosage)
- Ingredients breakdown table
- Validation status with color-coded badges
- Composition percentages

## 🧪 Testing

Test the formulation engine:

bash
# Search for a recipe
1. Type "gulab jamun" in the search bar
2. Select from autocomplete results
3. Set batch size (e.g., 1 kg)
4. Click "Generate Formulation"

# Expected output:
- ✅ 40-step SOP
- ✅ Water activity: ~0.72
- ✅ Shelf life: 12 weeks
- ✅ Viscosity: ~10.5 Pa·s
- ✅ Dosage: ~90 g/kg
- ✅ All validations PASS


## 🚢 Deployment

### Deploy to Reflex Cloud (Recommended)

bash
reflex deploy


### Environment Variables in Production

Set these in your deployment platform:
- `SUPABASE_URL`
- `SUPABASE_KEY`

## 📚 Documentation

- **[Plan](plan.md)** - Complete project roadmap and implementation phases
- **[Rules](rules.md)** - Master prompt with all coding standards and requirements
- **[Database Schema](app/database/schema.sql)** - Complete SQL schema with sample data

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- **Gelato Science Constants** - FICSI + IDF papers
- **Norrish Equation** - Water activity modeling (1966)
- **Reflex Framework** - Python web framework

## 📧 Contact

- **Repository:** https://github.com/koviddutta/paste-studio-mvp
- **Issues:** https://github.com/koviddutta/paste-studio-mvp/issues

---

**Built with ❤️ using [Reflex](https://reflex.dev)**
