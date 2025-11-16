# Paste Studio MVP - Indian Sweets Paste Formulation Engine

## Current Goal
Build a complete Indian sweets paste formulation system that:
- Fetches recipes from Supabase (1040+ Indian sweets) ✓
- Classifies ingredients into 6 processing classes (A-F)
- Generates detailed 40-step production SOPs
- Calculates properties (water activity, shelf-life, viscosity, gelato dosage)
- Runs safety validations
- Outputs downloadable PDF SOPs

---

## Phase 1: Supabase Database Setup and Connection ✅
- [x] Set up Supabase integration and test connection
- [x] Create database schema (ingredients_master, processing_rules, formulation_constants)
- [x] Seed initial data (ingredient classes, processing rules, sample recipes)
- [x] Create database query functions for recipes and ingredients
- [x] Test data retrieval with sample queries

**Note:** Schema SQL file created in app/database/schema.sql. Tables need to be created in Supabase dashboard - see app/database/README.md for instructions.

---

## Phase 2: Ingredient Classification Engine ✅
- [x] Build ingredient classifier with 6 classes (A-F: Dairy, Nut, Sugar, Fat, Stabilizer, Aromatic)
- [x] Implement ingredient properties (moisture, fat, protein percentages)
- [x] Create alias handling system (mawa → khoya)
- [x] Add processing parameters (temps, times, equipment) per class
- [x] Test classification with various ingredient names

**Implementation Complete:** 
- Created `app/engines/ingredient_classifier.py` with classification functions
- Created `app/database/schema.sql` with complete database schema
- Updated `app/database/supabase_client.py` with query functions
- Created comprehensive README for database setup

**User Action Required:** Run schema.sql in Supabase SQL Editor to create tables

---

## Phase 3: SOP Generation System
- [ ] Implement Universal 10-Step Algorithm for SOP generation
- [ ] Create detailed 40-step expansion logic with temps, times, equipment
- [ ] Add step sequencing based on ingredient classes
- [ ] Implement temperature rules enforcement (LBG at 85°C, fats at 65°C, aromatics <50°C)
- [ ] Generate formatted SOP output with safety checks

---

## Phase 4: Properties Calculator and Validators
- [ ] Implement Norrish equation for water activity calculation
- [ ] Add shelf-life estimation based on water activity
- [ ] Create viscosity calculator using power law model
- [ ] Build gelato dosage calculator
- [ ] Implement validation gates (Aw: 0.68-0.75, pH: 5.4-6.8, sugar: 20-40%, fat: 10-20%)

---

## Phase 5: FastAPI Backend Endpoints
- [ ] Create POST /api/formulation/generate endpoint
- [ ] Add GET /api/recipes/search with autocomplete
- [ ] Implement complete formulation generation pipeline
- [ ] Add error handling and validation responses
- [ ] Test all endpoints with sample data

---

## Phase 6: Frontend UI - Recipe Search and Selection
- [ ] Build recipe search page with autocomplete (1040+ recipes)
- [ ] Add batch size input field
- [ ] Create "Generate Formulation" button
- [ ] Display loading states during processing
- [ ] Implement navigation to formulation results

---

## Phase 7: Frontend UI - Formulation Display and SOP Viewer
- [ ] Create formulation display page (ingredients table, properties)
- [ ] Build 40-step SOP viewer with interactive checkboxes
- [ ] Add properties dashboard (Aw, shelf-life, viscosity, dosage)
- [ ] Implement PDF download functionality
- [ ] Create troubleshooting page with problem selector

---

## Phase 8: UI Verification and Testing
- [ ] Test complete flow: search → generate → view SOP
- [ ] Verify property calculations display correctly
- [ ] Test validation warnings for out-of-range values
- [ ] Validate PDF generation and download
- [ ] Test troubleshooting suggestions system
