# 🍬 Paste Studio MVP - Indian Sweets Formulation Engine

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Reflex](https://img.shields.io/badge/Reflex-0.8+-purple.svg)](https://reflex.dev)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready formulation engine for Indian sweets that converts traditional recipes into standardized, scientifically-validated paste formulations.

## ✨ Features

### 🔍 Recipe Database
- **1000+ Traditional Recipes** from Supabase database
- Real-time autocomplete search
- Batch size customization (kg)

### 🧪 Ingredient Classification
- **6 Processing Classes** (A-F):
  - A: Dairy (Khoya, Milk, Paneer)
  - B: Nuts (Pistachio, Almond, Cashew)
  - C: Sugars (Sucrose, Jaggery, Glucose)
  - D: Fats (Ghee, Oil, Butter)
  - E: Stabilizers (LBG, Guar, Lambda)
  - F: Aromatics (Cardamom, Saffron, Rose)

### 📋 SOP Generation
- **Detailed 40-step Production SOPs**
- Temperature controls (85°C for LBG, 65°C for fats, <50°C for aromatics)
- Time tracking for each step
- Equipment specifications
- Science-based reasoning

### 🔬 Property Calculators
- **Water Activity (Aw)** using Norrish equation
- **Shelf-life Estimation** (target: 12 weeks at Aw 0.68-0.75)
- **Viscosity Modeling** (Power law + Arrhenius)
- **Gelato Dosage Calculator**

### ✅ Validation System
- PASS/WARNING/FAIL status badges
- Safety checks (pasteurization for dairy)
- Composition validation (sugar, fat, stabilizer percentages)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Supabase account
- GitHub account (optional, for deployment)

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
   # Edit .env with your credentials:
   # SUPABASE_URL=your_supabase_url
   # SUPABASE_KEY=your_supabase_key
   

4. **Set up the database:**
   - Go to your Supabase Dashboard
   - Navigate to SQL Editor
   - Run the schema from `app/database/schema.sql`

5. **Run the application:**
   bash
   reflex run
   

6. **Open in browser:**
   
   http://localhost:3000
   

## 📊 Usage Example

1. **Search for a recipe** (e.g., "Gulab Jamun")
2. **Set batch size** (e.g., 1 kg)
3. **Generate formulation** - Get:
   - Ingredient breakdown with classifications
   - 40-step production SOP with temperatures & times
   - Water activity, shelf-life, viscosity calculations
   - Safety validation report

## 🗄️ Database Schema

The application requires these Supabase tables:

- `desserts_master_v2` - 1000+ Indian sweet recipes
- `ingredients_master` - Ingredient properties & classifications
- `processing_rules` - Step-by-step processing instructions
- `formulation_constants` - Scientific constants (Norrish K values, etc.)

See `app/database/schema.sql` for complete schema.

## 🏗️ Architecture


paste-studio-mvp/
├── app/
│   ├── app.py              # Main Reflex app
│   ├── components/         # UI components
│   ├── states/             # State management
│   ├── calculators/        # Property calculators
│   ├── engines/            # Classification & SOP logic
│   ├── validators/         # Formulation validators
│   └── database/           # Supabase integration
├── assets/                 # Static assets
├── requirements.txt
└── rxconfig.py


## 🔬 Core Algorithms

### Water Activity (Norrish Equation)

a_w = X_water × exp(-(K_sugar × X_sugar² + K_protein × X_protein²))
# K_sugar = 6.47, K_protein = 4.2


### Shelf-life Estimation
- Aw 0.68-0.75: ✅ 12 weeks (Safe)
- Aw 0.75-0.85: ⚠️ 4 weeks (Risky - slow mold)
- Aw >0.85: ❌ 1 week (Unsafe - fast mold)

## 🧪 Testing

Run the test suite:
bash
pytest


## 📝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Reflex** for the amazing Python web framework
- **Supabase** for the database infrastructure
- Traditional Indian sweet makers for the recipes

## 📧 Contact

**Kovid Dutta** - [GitHub](https://github.com/koviddutta)

---

**⭐ Star this repo** if you find it useful!

Built with ❤️ using [Reflex](https://reflex.dev)
