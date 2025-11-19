-- ================================================================
-- Paste Studio MVP - Supabase Database Schema
-- Indian Sweets Formulation Engine
-- ================================================================

-- ================================================================
-- Table 1: ingredients_master
-- Purpose: Master database of all ingredients with properties
-- ================================================================

CREATE TABLE IF NOT EXISTS ingredients_master (
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

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_ingredients_class ON ingredients_master(class);
CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients_master(name);

-- ================================================================
-- Table 2: processing_rules
-- Purpose: Step-by-step processing instructions by ingredient class
-- ================================================================

CREATE TABLE IF NOT EXISTS processing_rules (
  id SERIAL PRIMARY KEY,
  ingredient_class VARCHAR(20) NOT NULL,
  step_order INT NOT NULL,
  action VARCHAR(200),
  temperature_c INT,
  time_minutes INT,
  equipment VARCHAR(100),
  science_reason TEXT,
  UNIQUE(ingredient_class, step_order)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_processing_class ON processing_rules(ingredient_class);

-- ================================================================
-- Table 3: formulation_constants
-- Purpose: Scientific constants for property calculations
-- ================================================================

CREATE TABLE IF NOT EXISTS formulation_constants (
  constant_name VARCHAR(100) PRIMARY KEY,
  value FLOAT NOT NULL,
  unit VARCHAR(50),
  source TEXT
);

-- ================================================================
-- Table 4: gelato_science_constants
-- Purpose: Gelato University sugar science (AFP, SP, DE values)
-- ================================================================

CREATE TABLE IF NOT EXISTS gelato_science_constants (
  sugar_type VARCHAR(50) PRIMARY KEY,
  afp_value FLOAT NOT NULL,
  sp_value FLOAT NOT NULL,
  de_value FLOAT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ================================================================
-- Table 5: validation_thresholds
-- Purpose: Scientific validation thresholds for formulation quality
-- ================================================================

CREATE TABLE IF NOT EXISTS validation_thresholds (
  parameter_name VARCHAR(100) PRIMARY KEY,
  optimal_min FLOAT,
  optimal_max FLOAT,
  acceptable_min FLOAT,
  acceptable_max FLOAT,
  explanation TEXT
);

-- ================================================================
-- Table 6: msnf_stabilizer_balance
-- Purpose: MSNF and stabilizer balance thresholds by formulation type
-- ================================================================

CREATE TABLE IF NOT EXISTS msnf_stabilizer_balance (
  formulation_type VARCHAR(50) PRIMARY KEY,
  msnf_min_pct FLOAT,
  msnf_max_pct FLOAT,
  stabilizer_min_pct FLOAT,
  stabilizer_max_pct FLOAT,
  explanation TEXT
);

-- ================================================================
-- SEED DATA - Ingredients Master
-- ================================================================

-- Class A: DAIRY
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('khoya', 'A_DAIRY', ARRAY['mawa', 'khoa'], 30.0, 25.0, 15.0, 5.0, 85, 30, 'Blender'),
('milk', 'A_DAIRY', ARRAY['full cream milk', 'whole milk'], 87.0, 3.5, 3.3, 4.8, 85, 30, 'Pot'),
('paneer', 'A_DAIRY', ARRAY['cottage cheese'], 50.0, 20.0, 18.0, 2.5, 85, 30, 'Blender'),
('cream', 'A_DAIRY', ARRAY['heavy cream', 'whipping cream'], 60.0, 35.0, 2.5, 3.0, 85, 30, 'Mixer'),
('condensed milk', 'A_DAIRY', ARRAY['sweetened condensed milk'], 27.0, 8.0, 7.5, 54.0, 85, 30, 'Pot')
ON CONFLICT (name) DO NOTHING;

-- Class B: NUTS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('pistachio', 'B_NUT', ARRAY['pista'], 4.0, 45.0, 20.0, 7.0, 120, 10, 'Wet Grinder'),
('almond', 'B_NUT', ARRAY['badam'], 4.5, 50.0, 21.0, 4.0, 120, 10, 'Wet Grinder'),
('cashew', 'B_NUT', ARRAY['kaju'], 5.0, 44.0, 18.0, 6.0, 120, 10, 'Wet Grinder'),
('walnut', 'B_NUT', ARRAY['akhrot'], 4.0, 65.0, 15.0, 2.5, 120, 10, 'Wet Grinder')
ON CONFLICT (name) DO NOTHING;

-- Class C: SUGARS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('sugar', 'C_SUGAR', ARRAY['sucrose', 'white sugar'], 0.5, 0.0, 0.0, 99.5, 70, 5, 'Pot'),
('jaggery', 'C_SUGAR', ARRAY['gur', 'gud'], 5.0, 0.0, 0.0, 92.0, 70, 5, 'Pot'),
('glucose', 'C_SUGAR', ARRAY['liquid glucose', 'glucose syrup'], 20.0, 0.0, 0.0, 80.0, 70, 5, 'Pot')
ON CONFLICT (name) DO NOTHING;

-- Class D: FATS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('ghee', 'D_FAT', ARRAY['clarified butter'], 0.5, 99.5, 0.0, 0.0, 65, 2, 'Mixer'),
('butter', 'D_FAT', ARRAY['unsalted butter'], 15.0, 81.0, 1.0, 0.5, 65, 2, 'Mixer'),
('oil', 'D_FAT', ARRAY['vegetable oil', 'sunflower oil'], 0.0, 100.0, 0.0, 0.0, 65, 2, 'Mixer'),
('cocoa butter', 'D_FAT', ARRAY[], 0.0, 100.0, 0.0, 0.0, 65, 2, 'Mixer')
ON CONFLICT (name) DO NOTHING;

-- Class E: STABILIZERS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('lbg', 'E_STABILIZER', ARRAY['locust bean gum', 'carob gum'], 0.0, 0.0, 0.0, 0.0, 85, 5, 'High-shear Mixer'),
('guar gum', 'E_STABILIZER', ARRAY['guar'], 0.0, 0.0, 0.0, 0.0, 40, 60, 'Mixer'),
('lambda carrageenan', 'E_STABILIZER', ARRAY['lambda'], 0.0, 0.0, 0.0, 0.0, 65, 3, 'Mixer'),
('xanthan gum', 'E_STABILIZER', ARRAY['xanthan'], 0.0, 0.0, 0.0, 0.0, 85, 5, 'High-shear Mixer')
ON CONFLICT (name) DO NOTHING;

-- Class F: AROMATICS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('cardamom', 'F_AROMATIC', ARRAY['elaichi', 'green cardamom'], 8.0, 2.0, 10.0, 0.0, 50, 1, 'Grinder'),
('saffron', 'F_AROMATIC', ARRAY['kesar'], 10.0, 5.0, 11.0, 0.0, 50, 1, 'None'),
('rose water', 'F_AROMATIC', ARRAY['rose essence'], 95.0, 0.0, 0.0, 0.0, 50, 1, 'None'),
('vanilla', 'F_AROMATIC', ARRAY['vanilla extract'], 35.0, 0.0, 0.0, 10.0, 50, 1, 'None')
ON CONFLICT (name) DO NOTHING;

-- ================================================================
-- SEED DATA - Processing Rules
-- ================================================================

-- Class A: DAIRY Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('A_DAIRY', 1, 'Crumble or measure dairy ingredients', 25, 5, 'Bowl', 'Room temperature handling prevents premature spoilage'),
('A_DAIRY', 2, 'Heat water for aqueous phase', 60, 5, 'Pot', 'Warm water aids sugar dissolution'),
('A_DAIRY', 3, 'Pasteurize dairy at 85°C for 30 seconds', 85, 2, 'Pot', 'Kills pathogenic bacteria (Salmonella, Listeria, E. coli)'),
('A_DAIRY', 4, 'Blend dairy into smooth paste', 85, 3, 'Blender', 'Homogenization creates uniform texture'),
('A_DAIRY', 5, 'Hold temperature for protein denaturation', 85, 5, 'Pot', 'Protein unfolding improves water binding')
ON CONFLICT (ingredient_class, step_order) DO NOTHING;

-- Class B: NUT Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('B_NUT', 1, 'Roast nuts to develop flavor', 120, 10, 'Oven', 'Maillard reaction creates nutty aroma compounds'),
('B_NUT', 2, 'Cool nuts to room temperature', 25, 5, 'Tray', 'Prevents heat damage during grinding'),
('B_NUT', 3, 'Grind nuts to <40μm particle size', 25, 10, 'Wet Grinder', 'Fine particles create smooth mouthfeel'),
('B_NUT', 4, 'Add to main mixture gradually', 85, 3, 'Mixer', 'Gradual addition prevents clumping')
ON CONFLICT (ingredient_class, step_order) DO NOTHING;

-- Class C: SUGAR Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('C_SUGAR', 1, 'Dissolve sugar in warm water', 70, 5, 'Pot', 'Heat accelerates dissolution rate'),
('C_SUGAR', 2, 'Stir until no grains visible', 70, 3, 'Pot', 'Complete dissolution prevents crystallization'),
('C_SUGAR', 3, 'Add to dairy mixture', 85, 2, 'Mixer', 'Sugar lowers water activity (preservation)')
ON CONFLICT (ingredient_class, step_order) DO NOTHING;

-- Class D: FAT Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('D_FAT', 1, 'Melt fat gently', 50, 2, 'Pot', 'Gentle melting preserves flavor compounds'),
('D_FAT', 2, 'Cool to emulsification temperature', 65, 1, 'Pot', '65°C optimal for stable emulsion formation'),
('D_FAT', 3, 'Add slowly with high-shear mixing', 65, 2, 'High-shear Mixer', 'Shear breaks fat into <2μm droplets for stability')
ON CONFLICT (ingredient_class, step_order) DO NOTHING;

-- Class E: STABILIZER Processing Rules (Sequential Hydration)
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('E_STABILIZER', 1, 'Hydrate LBG at 85°C with high-shear', 85, 5, 'High-shear Mixer', 'LBG requires heat to break crystal structure and hydrate'),
('E_STABILIZER', 2, 'Cool to 65°C and add Lambda', 65, 3, 'Mixer', 'Lambda hydrates best at 65°C, creates elastic gel'),
('E_STABILIZER', 3, 'Cool to 40°C and add Guar gum', 40, 60, 'Mixer', 'Guar hydrates slowly at low temp, prevents lumps')
ON CONFLICT (ingredient_class, step_order) DO NOTHING;

-- Class F: AROMATIC Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('F_AROMATIC', 1, 'Grind whole spices if needed', 25, 1, 'Grinder', 'Fresh grinding maximizes volatile oil release'),
('F_AROMATIC', 2, 'Cool mixture to <50°C', 50, 10, 'None', 'Heat degrades volatile aroma compounds'),
('F_AROMATIC', 3, 'Add aromatics gently', 50, 1, 'Spoon', 'Gentle mixing preserves delicate compounds'),
('F_AROMATIC', 4, 'Final cooling to storage temperature', 25, 21, 'None', 'Room temperature prevents condensation')
ON CONFLICT (ingredient_class, step_order) DO NOTHING;

-- ================================================================
-- SEED DATA - Formulation Constants
-- ================================================================

-- Norrish Equation Constants (Water Activity Calculation)
INSERT INTO formulation_constants (constant_name, value, unit, source) VALUES
('K_SUGAR_NORRISH', 6.47, 'dimensionless', 'Norrish (1966) - Sugar depression constant'),
('K_PROTEIN_NORRISH', 4.2, 'dimensionless', 'Norrish (1966) - Protein depression constant')
ON CONFLICT (constant_name) DO NOTHING;

-- Viscosity Model Constants (Power Law + Arrhenius)
INSERT INTO formulation_constants (constant_name, value, unit, source) VALUES
('VISC_K_CONSISTENCY', 0.5, 'Pa·s^n', 'Power law consistency index for paste systems'),
('VISC_N_FLOW_INDEX', 0.8, 'dimensionless', 'Flow behavior index (shear thinning)'),
('VISC_E_ACTIVATION', 20000.0, 'J/mol', 'Arrhenius activation energy for viscosity'),
('VISC_SHEAR_RATE', 10.0, '1/s', 'Standard shear rate for measurement'),
('VISC_REF_TEMP_K', 293.15, 'K', 'Reference temperature (20°C)')
ON CONFLICT (constant_name) DO NOTHING;

-- Molar Mass Constants
INSERT INTO formulation_constants (constant_name, value, unit, source) VALUES
('MOLAR_MASS_WATER', 18.015, 'g/mol', 'Standard water molecular weight'),
('MOLAR_MASS_SUGAR', 342.3, 'g/mol', 'Sucrose (C12H22O11)'),
('MOLAR_MASS_PROTEIN', 1000.0, 'g/mol', 'Estimated average for dairy proteins')
ON CONFLICT (constant_name) DO NOTHING;

-- ================================================================
-- SEED DATA - Gelato Science Constants (Gelato University Standards)
-- ================================================================

INSERT INTO gelato_science_constants (sugar_type, afp_value, sp_value, de_value) VALUES
('sucrose', 100.0, 100.0, 100.0),
('dextrose', 190.0, 95.0, 100.0),
('fructose', 190.0, 173.0, 100.0),
('invert_sugar', 190.0, 130.0, 95.0),
('lactose', 16.0, 23.0, 100.0),
('maltose', 48.0, 38.0, 100.0),
('honey', 180.0, 100.0, 85.0),
('maple_syrup', 155.0, 84.0, 85.0),
('glucose_de21', 48.0, 55.0, 21.0),
('glucose_de38', 75.0, 85.0, 38.0),
('glucose_de45', 90.0, 95.0, 45.0),
('glucose_de63', 130.0, 120.0, 63.0),
('isomalt', 5.0, 50.0, 100.0),
('sorbitol', 5.0, 100.0, 100.0)
ON CONFLICT (sugar_type) DO NOTHING;

-- ================================================================
-- SEED DATA - Validation Thresholds
-- ================================================================

INSERT INTO validation_thresholds (parameter_name, optimal_min, optimal_max, acceptable_min, acceptable_max, explanation) VALUES
('afp_total', 200.0, 300.0, 180.0, 350.0, 'Total anti-freezing power (AFP) controls ice crystallization'),
('sp_total', 16.5, 22.5, 14.0, 24.0, 'Sweetness power (SP) controls perceived sweetness'),
('pod_total', 28.0, 39.0, 25.0, 42.0, 'Power of dextrose (POD) controls scoopability and texture'),
('de_balance', 65.0, 75.0, 60.0, 80.0, 'Dextrose equivalent (DE) balance for optimal freezing'),
('pac_total', 325.0, 425.0, 300.0, 450.0, 'Total PAC (AFP + POD + SP/5) for complete formulation balance'),
('total_solids_pct', 32.0, 40.0, 28.0, 42.0, 'Total solids percentage for proper body and texture'),
('fat_pct', 6.0, 12.0, 4.0, 16.0, 'Fat content for creaminess and mouthfeel'),
('msnf_pct', 8.0, 12.0, 6.0, 14.0, 'Milk solids non-fat for body and sweetness'),
('water_activity', 0.68, 0.75, 0.65, 0.80, 'Water activity (Aw) for microbial safety and shelf life'),
('shelf_life_weeks', 10.0, 14.0, 8.0, 16.0, 'Expected shelf life in weeks at proper storage'),
('stabilizer_pct', 0.3, 0.6, 0.2, 0.8, 'Stabilizer content for texture and meltdown control')
ON CONFLICT (parameter_name) DO NOTHING;

-- ================================================================
-- SEED DATA - MSNF & Stabilizer Balance Thresholds
-- ================================================================

INSERT INTO msnf_stabilizer_balance (formulation_type, msnf_min_pct, msnf_max_pct, stabilizer_min_pct, stabilizer_max_pct, explanation) VALUES
('cocoa_chocolate', 7.0, 9.0, 0.4, 0.6, 'Cocoa/chocolate based: Lower MSNF, higher stabilizer for richness'),
('eggs_nuts', 8.0, 10.0, 0.3, 0.5, 'Egg/nut based: Moderate MSNF, moderate stabilizer'),
('dairy_fruit', 9.0, 11.0, 0.35, 0.55, 'Dairy-fruit mix: Higher MSNF for balance'),
('pure_dairy', 10.0, 13.0, 0.3, 0.5, 'Pure dairy: Highest MSNF for traditional texture'),
('fruit_sorbet', 0.0, 2.0, 0.5, 0.8, 'Fruit sorbet: Minimal MSNF, highest stabilizer for structure')
ON CONFLICT (formulation_type) DO NOTHING;

-- ================================================================
-- VERIFICATION QUERIES (Run these after setup)
-- ================================================================

-- Check if tables were created
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('ingredients_master', 'processing_rules', 'formulation_constants', 'gelato_science_constants', 'validation_thresholds', 'msnf_stabilizer_balance');

-- Count records in each table
-- SELECT 'ingredients_master' as table_name, COUNT(*) as records FROM ingredients_master
-- UNION ALL
-- SELECT 'processing_rules', COUNT(*) FROM processing_rules
-- UNION ALL
-- SELECT 'formulation_constants', COUNT(*) FROM formulation_constants
-- UNION ALL
-- SELECT 'gelato_science_constants', COUNT(*) FROM gelato_science_constants
-- UNION ALL
-- SELECT 'validation_thresholds', COUNT(*) FROM validation_thresholds
-- UNION ALL
-- SELECT 'msnf_stabilizer_balance', COUNT(*) FROM msnf_stabilizer_balance;

-- ================================================================
-- SETUP COMPLETE! 
-- ================================================================
-- Tables Created:
--   ✓ ingredients_master (23 ingredients across 6 classes)
--   ✓ processing_rules (22 processing steps)
--   ✓ formulation_constants (10 scientific constants)
--   ✓ gelato_science_constants (14 sugar types with AFP/SP/DE)
--   ✓ validation_thresholds (11 scientific parameters)
--   ✓ msnf_stabilizer_balance (5 formulation types)
--
-- Next Steps:
--   1. Verify tables exist in Supabase Table Editor
--   2. Test your app with recipe search
--   3. Generate your first formulation!
-- ================================================================
