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
-- SEED DATA - Ingredients Master
-- ================================================================

-- Class A: DAIRY
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('khoya', 'A_DAIRY', ARRAY['mawa', 'khoa'], 30.0, 25.0, 15.0, 5.0, 85, 30, 'Blender'),
('milk', 'A_DAIRY', ARRAY['full cream milk', 'whole milk'], 87.0, 3.5, 3.3, 4.8, 85, 30, 'Pot'),
('paneer', 'A_DAIRY', ARRAY['cottage cheese'], 50.0, 20.0, 18.0, 2.5, 85, 30, 'Blender'),
('cream', 'A_DAIRY', ARRAY['heavy cream', 'whipping cream'], 60.0, 35.0, 2.5, 3.0, 85, 30, 'Mixer'),
('condensed milk', 'A_DAIRY', ARRAY['sweetened condensed milk'], 27.0, 8.0, 7.5, 54.0, 85, 30, 'Pot');

-- Class B: NUTS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('pistachio', 'B_NUT', ARRAY['pista'], 4.0, 45.0, 20.0, 7.0, 120, 10, 'Wet Grinder'),
('almond', 'B_NUT', ARRAY['badam'], 4.5, 50.0, 21.0, 4.0, 120, 10, 'Wet Grinder'),
('cashew', 'B_NUT', ARRAY['kaju'], 5.0, 44.0, 18.0, 6.0, 120, 10, 'Wet Grinder'),
('walnut', 'B_NUT', ARRAY['akhrot'], 4.0, 65.0, 15.0, 2.5, 120, 10, 'Wet Grinder');

-- Class C: SUGARS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('sugar', 'C_SUGAR', ARRAY['sucrose', 'white sugar'], 0.5, 0.0, 0.0, 99.5, 70, 5, 'Pot'),
('jaggery', 'C_SUGAR', ARRAY['gur', 'gud'], 5.0, 0.0, 0.0, 92.0, 70, 5, 'Pot'),
('glucose', 'C_SUGAR', ARRAY['liquid glucose', 'glucose syrup'], 20.0, 0.0, 0.0, 80.0, 70, 5, 'Pot');

-- Class D: FATS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('ghee', 'D_FAT', ARRAY['clarified butter'], 0.5, 99.5, 0.0, 0.0, 65, 2, 'Mixer'),
('butter', 'D_FAT', ARRAY['unsalted butter'], 15.0, 81.0, 1.0, 0.5, 65, 2, 'Mixer'),
('oil', 'D_FAT', ARRAY['vegetable oil', 'sunflower oil'], 0.0, 100.0, 0.0, 0.0, 65, 2, 'Mixer'),
('cocoa butter', 'D_FAT', ARRAY[], 0.0, 100.0, 0.0, 0.0, 65, 2, 'Mixer');

-- Class E: STABILIZERS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('lbg', 'E_STABILIZER', ARRAY['locust bean gum', 'carob gum'], 0.0, 0.0, 0.0, 0.0, 85, 5, 'High-shear Mixer'),
('guar gum', 'E_STABILIZER', ARRAY['guar'], 0.0, 0.0, 0.0, 0.0, 40, 60, 'Mixer'),
('lambda carrageenan', 'E_STABILIZER', ARRAY['lambda'], 0.0, 0.0, 0.0, 0.0, 65, 3, 'Mixer'),
('xanthan gum', 'E_STABILIZER', ARRAY['xanthan'], 0.0, 0.0, 0.0, 0.0, 85, 5, 'High-shear Mixer');

-- Class F: AROMATICS
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type) VALUES
('cardamom', 'F_AROMATIC', ARRAY['elaichi', 'green cardamom'], 8.0, 2.0, 10.0, 0.0, 50, 1, 'Grinder'),
('saffron', 'F_AROMATIC', ARRAY['kesar'], 10.0, 5.0, 11.0, 0.0, 50, 1, 'None'),
('rose water', 'F_AROMATIC', ARRAY['rose essence'], 95.0, 0.0, 0.0, 0.0, 50, 1, 'None'),
('vanilla', 'F_AROMATIC', ARRAY['vanilla extract'], 35.0, 0.0, 0.0, 10.0, 50, 1, 'None');

-- ================================================================
-- SEED DATA - Processing Rules
-- ================================================================

-- Class A: DAIRY Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('A_DAIRY', 1, 'Crumble or measure dairy ingredients', 25, 5, 'Bowl', 'Room temperature handling prevents premature spoilage'),
('A_DAIRY', 2, 'Heat water for aqueous phase', 60, 5, 'Pot', 'Warm water aids sugar dissolution'),
('A_DAIRY', 3, 'Pasteurize dairy at 85°C for 30 seconds', 85, 2, 'Pot', 'Kills pathogenic bacteria (Salmonella, Listeria, E. coli)'),
('A_DAIRY', 4, 'Blend dairy into smooth paste', 85, 3, 'Blender', 'Homogenization creates uniform texture'),
('A_DAIRY', 5, 'Hold temperature for protein denaturation', 85, 5, 'Pot', 'Protein unfolding improves water binding');

-- Class B: NUT Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('B_NUT', 1, 'Roast nuts to develop flavor', 120, 10, 'Oven', 'Maillard reaction creates nutty aroma compounds'),
('B_NUT', 2, 'Cool nuts to room temperature', 25, 5, 'Tray', 'Prevents heat damage during grinding'),
('B_NUT', 3, 'Grind nuts to <40μm particle size', 25, 10, 'Wet Grinder', 'Fine particles create smooth mouthfeel'),
('B_NUT', 4, 'Add to main mixture gradually', 85, 3, 'Mixer', 'Gradual addition prevents clumping');

-- Class C: SUGAR Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('C_SUGAR', 1, 'Dissolve sugar in warm water', 70, 5, 'Pot', 'Heat accelerates dissolution rate'),
('C_SUGAR', 2, 'Stir until no grains visible', 70, 3, 'Pot', 'Complete dissolution prevents crystallization'),
('C_SUGAR', 3, 'Add to dairy mixture', 85, 2, 'Mixer', 'Sugar lowers water activity (preservation)');

-- Class D: FAT Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('D_FAT', 1, 'Melt fat gently', 50, 2, 'Pot', 'Gentle melting preserves flavor compounds'),
('D_FAT', 2, 'Cool to emulsification temperature', 65, 1, 'Pot', '65°C optimal for stable emulsion formation'),
('D_FAT', 3, 'Add slowly with high-shear mixing', 65, 2, 'High-shear Mixer', 'Shear breaks fat into <2μm droplets for stability');

-- Class E: STABILIZER Processing Rules (Sequential Hydration)
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('E_STABILIZER', 1, 'Hydrate LBG at 85°C with high-shear', 85, 5, 'High-shear Mixer', 'LBG requires heat to break crystal structure and hydrate'),
('E_STABILIZER', 2, 'Cool to 65°C and add Lambda', 65, 3, 'Mixer', 'Lambda hydrates best at 65°C, creates elastic gel'),
('E_STABILIZER', 3, 'Cool to 40°C and add Guar gum', 40, 60, 'Mixer', 'Guar hydrates slowly at low temp, prevents lumps');

-- Class F: AROMATIC Processing Rules
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason) VALUES
('F_AROMATIC', 1, 'Grind whole spices if needed', 25, 1, 'Grinder', 'Fresh grinding maximizes volatile oil release'),
('F_AROMATIC', 2, 'Cool mixture to <50°C', 50, 10, 'None', 'Heat degrades volatile aroma compounds'),
('F_AROMATIC', 3, 'Add aromatics gently', 50, 1, 'Spoon', 'Gentle mixing preserves delicate compounds'),
('F_AROMATIC', 4, 'Final cooling to storage temperature', 25, 21, 'None', 'Room temperature prevents condensation');

-- ================================================================
-- SEED DATA - Formulation Constants
-- ================================================================

-- Norrish Equation Constants (Water Activity Calculation)
INSERT INTO formulation_constants (constant_name, value, unit, source) VALUES
('K_SUGAR_NORRISH', 6.47, 'dimensionless', 'Norrish (1966) - Sugar depression constant'),
('K_PROTEIN_NORRISH', 4.2, 'dimensionless', 'Norrish (1966) - Protein depression constant');

-- Viscosity Model Constants (Power Law + Arrhenius)
INSERT INTO formulation_constants (constant_name, value, unit, source) VALUES
('VISC_K_CONSISTENCY', 0.5, 'Pa·s^n', 'Power law consistency index for paste systems'),
('VISC_N_FLOW_INDEX', 0.8, 'dimensionless', 'Flow behavior index (shear thinning)'),
('VISC_E_ACTIVATION', 20000.0, 'J/mol', 'Arrhenius activation energy for viscosity'),
('VISC_SHEAR_RATE', 10.0, '1/s', 'Standard shear rate for measurement'),
('VISC_REF_TEMP_K', 293.15, 'K', 'Reference temperature (20°C)');

-- Molar Mass Constants
INSERT INTO formulation_constants (constant_name, value, unit, source) VALUES
('MOLAR_MASS_WATER', 18.015, 'g/mol', 'Standard water molecular weight'),
('MOLAR_MASS_SUGAR', 342.3, 'g/mol', 'Sucrose (C12H22O11)'),
('MOLAR_MASS_PROTEIN', 1000.0, 'g/mol', 'Estimated average for dairy proteins');

-- ================================================================
-- VERIFICATION QUERIES (Run these after setup)
-- ================================================================

-- Check if tables were created
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('ingredients_master', 'processing_rules', 'formulation_constants');

-- Count records in each table
-- SELECT 'ingredients_master' as table_name, COUNT(*) as records FROM ingredients_master
-- UNION ALL
-- SELECT 'processing_rules', COUNT(*) FROM processing_rules
-- UNION ALL
-- SELECT 'formulation_constants', COUNT(*) FROM formulation_constants;

-- Test ingredient classification
-- SELECT name, class, moisture_pct, fat_pct FROM ingredients_master WHERE class = 'A_DAIRY';

-- ================================================================
-- SETUP COMPLETE! 
-- ================================================================
-- Tables Created:
--   ✅ ingredients_master (23 ingredients across 6 classes)
--   ✅ processing_rules (22 processing steps)
--   ✅ formulation_constants (10 scientific constants)
--
-- Next Steps:
--   1. Verify tables exist in Supabase Table Editor
--   2. Test your app with recipe search
--   3. Generate your first formulation!
-- ================================================================
