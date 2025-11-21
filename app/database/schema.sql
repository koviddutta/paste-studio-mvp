-- Paste Studio MVP Database Schema
-- Indian Sweets Formulation Engine
-- Run this in your Supabase SQL Editor

-- ============================================
-- 1. INGREDIENTS MASTER TABLE
-- ============================================
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

-- Sample ingredient data
INSERT INTO ingredients_master (name, class, aliases, moisture_pct, fat_pct, protein_pct, sugar_pct, processing_temp_c, processing_time_min, equipment_type)
VALUES
  ('khoya', 'A_DAIRY', ARRAY['mawa', 'khoa'], 20.0, 30.0, 20.0, 0.0, 85, 30, 'Blender'),
  ('milk', 'A_DAIRY', ARRAY['whole milk'], 87.0, 4.0, 3.5, 5.0, 85, 30, 'Pot'),
  ('sugar', 'C_SUGAR', ARRAY['sucrose', 'white sugar'], 0.0, 0.0, 0.0, 100.0, 60, 5, 'Pot'),
  ('ghee', 'D_FAT', ARRAY['clarified butter'], 0.0, 99.5, 0.0, 0.0, 50, 2, 'Pot'),
  ('cardamom', 'F_AROMATIC', ARRAY['elaichi'], 10.0, 0.0, 0.0, 0.0, 25, 1, 'Grinder'),
  ('pistachio', 'B_NUT', ARRAY['pista'], 4.0, 45.0, 20.0, 0.0, 120, 10, 'Grinder'),
  ('almond', 'B_NUT', ARRAY['badam'], 5.0, 50.0, 21.0, 0.0, 120, 10, 'Grinder'),
  ('saffron', 'F_AROMATIC', ARRAY['kesar'], 10.0, 0.0, 0.0, 0.0, 25, 1, 'Bowl'),
  ('rose water', 'F_AROMATIC', ARRAY['gulab jal'], 95.0, 0.0, 0.0, 0.0, 25, 1, 'Bottle'),
  ('paneer', 'A_DAIRY', ARRAY['cottage cheese'], 55.0, 20.0, 18.0, 2.0, 85, 30, 'Blender')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- 2. PROCESSING RULES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS processing_rules (
  id SERIAL PRIMARY KEY,
  ingredient_class VARCHAR(20) NOT NULL,
  step_order INT NOT NULL,
  action VARCHAR(200),
  temperature_c INT,
  time_minutes INT,
  equipment VARCHAR(100),
  science_reason TEXT
);

-- Insert processing rules for each ingredient class
INSERT INTO processing_rules (ingredient_class, step_order, action, temperature_c, time_minutes, equipment, science_reason)
VALUES
  -- Class A: DAIRY
  ('A_DAIRY', 1, 'Heat milk/dairy base', 85, 2, 'Pot', 'Pasteurization kills pathogens (72°C minimum)'),
  ('A_DAIRY', 2, 'Hold at temperature', 85, 0.5, 'Pot', 'Ensure complete pasteurization'),
  ('A_DAIRY', 3, 'Add to base mixture', 85, 3, 'Blender', 'Incorporate while hot for emulsification'),
  
  -- Class B: NUTS
  ('B_NUT', 1, 'Roast nuts', 120, 10, 'Oven', 'Develops flavor, reduces moisture'),
  ('B_NUT', 2, 'Grind to fine paste', 40, 5, 'Wet grinder', 'Particle size <40μm for smooth texture'),
  ('B_NUT', 3, 'Add to cooled base', 40, 2, 'Mixer', 'Prevents oil separation from heat'),
  
  -- Class C: SUGARS
  ('C_SUGAR', 1, 'Dissolve in water', 60, 5, 'Pot', 'Complete dissolution prevents crystallization'),
  ('C_SUGAR', 2, 'Bring to target temperature', 70, 3, 'Pot', 'Optimal sugar solution temperature'),
  
  -- Class D: FATS
  ('D_FAT', 1, 'Melt fat gently', 50, 2, 'Pot', 'Gentle heating preserves flavor'),
  ('D_FAT', 2, 'Emulsify into base', 65, 1.5, 'High-shear mixer', 'High shear creates stable emulsion'),
  
  -- Class E: STABILIZERS
  ('E_STABILIZER', 1, 'Hydrate stabilizer', 85, 5, 'High-shear mixer', 'LBG requires 85°C for hydration'),
  ('E_STABILIZER', 2, 'Cool and maintain mixing', 40, 60, 'Mixer', 'Allows full hydration as solution cools'),
  
  -- Class F: AROMATICS
  ('F_AROMATIC', 1, 'Add aromatics last', 25, 1, 'Bowl', 'Volatile compounds lost above 50°C'),
  ('F_AROMATIC', 2, 'Gentle mixing', 25, 2, 'Spoon', 'Preserves delicate flavor compounds')
ON CONFLICT DO NOTHING;

-- ============================================
-- 3. FORMULATION CONSTANTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS formulation_constants (
  constant_name VARCHAR(100) PRIMARY KEY,
  value FLOAT NOT NULL,
  unit VARCHAR(50),
  source TEXT
);

-- Insert scientific constants for calculations
INSERT INTO formulation_constants (constant_name, value, unit, source)
VALUES
  -- Norrish equation constants
  ('K_SUGAR_NORRISH', 6.47, 'dimensionless', 'Norrish 1966 water activity model'),
  ('K_PROTEIN_NORRISH', 4.2, 'dimensionless', 'Modified Norrish for protein systems'),
  
  -- Viscosity model constants
  ('VISC_K_CONSISTENCY', 0.5, 'Pa·s^n', 'Power law consistency index'),
  ('VISC_N_FLOW_INDEX', 0.8, 'dimensionless', 'Flow behavior index (shear thinning)'),
  ('VISC_E_ACTIVATION', 20000.0, 'J/mol', 'Arrhenius activation energy'),
  ('VISC_SHEAR_RATE', 10.0, '1/s', 'Reference shear rate for measurement'),
  ('VISC_REF_TEMP_K', 293.15, 'K', 'Reference temperature (20°C)'),
  
  -- Water activity targets
  ('AW_TARGET_MIN', 0.68, 'aw', 'Minimum safe water activity'),
  ('AW_TARGET_MAX', 0.75, 'aw', 'Maximum optimal water activity'),
  
  -- Composition targets
  ('SUGAR_PCT_MIN', 20.0, '%', 'Minimum sugar content'),
  ('SUGAR_PCT_MAX', 40.0, '%', 'Maximum sugar content'),
  ('FAT_PCT_MIN', 10.0, '%', 'Minimum fat content'),
  ('FAT_PCT_MAX', 20.0, '%', 'Maximum fat content'),
  ('STABILIZER_PCT_MIN', 0.25, '%', 'Minimum stabilizer'),
  ('STABILIZER_PCT_MAX', 0.50, '%', 'Maximum stabilizer')
ON CONFLICT (constant_name) DO UPDATE SET value = EXCLUDED.value;

-- ============================================
-- VERIFICATION QUERY
-- ============================================
-- Run this to verify all tables were created:
SELECT 
  'ingredients_master' as table_name, COUNT(*) as row_count FROM ingredients_master
UNION ALL
SELECT 'processing_rules', COUNT(*) FROM processing_rules
UNION ALL
SELECT 'formulation_constants', COUNT(*) FROM formulation_constants;

-- Expected output:
-- ingredients_master: 10 rows
-- processing_rules: 14 rows
-- formulation_constants: 16 rows
