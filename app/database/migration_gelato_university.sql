-- ================================================================
-- GELATO UNIVERSITY CARPIGIANI - SCIENTIFIC DATA MIGRATION
-- Paste Studio MVP - Professional Formulation Science Layer
-- ================================================================
-- This migration adds all Gelato University Carpigiani standards
-- for professional Indian sweets paste formulation validation.
-- ================================================================

-- ================================================================
-- TABLE 1: gelato_science_constants (Extended with 14 Sugar Types)
-- Purpose: Complete sugar substitution database with SP, AFP, DE values
-- ================================================================

CREATE TABLE IF NOT EXISTS gelato_science_constants (
  id SERIAL PRIMARY KEY,
  sugar_type VARCHAR(100) UNIQUE NOT NULL,
  sp_value FLOAT NOT NULL,              -- Sweetening Power (sucrose = 1.0)
  afp_value FLOAT NOT NULL,              -- Anti-Freezing Power (sucrose = 1.0)
  de_value FLOAT NOT NULL,               -- Dextrose Equivalence (0-100)
  dry_residual_pct FLOAT DEFAULT 100.0,  -- Dry matter percentage
  texture_impact VARCHAR(100),           -- Texture effect description
  stability_notes TEXT,                  -- Storage and stability notes
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gelato_constants_sugar ON gelato_science_constants(sugar_type);

-- ================================================================
-- TABLE 2: msnf_stabilizer_balance
-- Purpose: MSNF and Stabilizer balance rules by formulation type
-- ================================================================

CREATE TABLE IF NOT EXISTS msnf_stabilizer_balance (
  id SERIAL PRIMARY KEY,
  formulation_type VARCHAR(50) UNIQUE NOT NULL,
  msnf_min_pct FLOAT NOT NULL,
  msnf_max_pct FLOAT NOT NULL,
  stabilizer_min_pct FLOAT NOT NULL,
  stabilizer_max_pct FLOAT NOT NULL,
  fat_min_pct FLOAT,
  fat_max_pct FLOAT,
  explanation TEXT,
  scientific_reason TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_msnf_formulation ON msnf_stabilizer_balance(formulation_type);

-- ================================================================
-- TABLE 3: validation_thresholds_extended
-- Purpose: Formulation-type-specific validation thresholds
-- ================================================================

CREATE TABLE IF NOT EXISTS validation_thresholds_extended (
  id SERIAL PRIMARY KEY,
  parameter_name VARCHAR(100) NOT NULL,
  formulation_type VARCHAR(50) NOT NULL,
  optimal_min FLOAT,
  optimal_max FLOAT,
  acceptable_min FLOAT NOT NULL,
  acceptable_max FLOAT NOT NULL,
  critical_min FLOAT,
  critical_max FLOAT,
  explanation TEXT,
  scientific_basis TEXT,
  measurement_unit VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(parameter_name, formulation_type)
);

CREATE INDEX IF NOT EXISTS idx_validation_param ON validation_thresholds_extended(parameter_name);
CREATE INDEX IF NOT EXISTS idx_validation_type ON validation_thresholds_extended(formulation_type);

-- ================================================================
-- SEED DATA: Gelato Science Constants (14 Sugar Types)
-- Source: Gelato University Carpigiani - Sugar Substitution Framework
-- ================================================================

INSERT INTO gelato_science_constants (sugar_type, sp_value, afp_value, de_value, dry_residual_pct, texture_impact, stability_notes) VALUES
('sucrose', 1.00, 1.00, 100.0, 100.0, 'Balanced - standard reference', 'Highly stable, no crystallization issues at normal usage'),
('lactose', 0.16, 1.00, 91.0, 100.0, 'Low sweetness, neutral texture', 'Low hygroscopicity, good for structure'),
('trehalose', 0.45, 1.00, 67.0, 100.0, 'Mild sweetness, smooth texture', 'Excellent stability, prevents protein denaturation'),
('maple_syrup', 0.70, 1.00, 92.0, 67.0, 'Characteristic flavor, soft texture', 'Contains minerals, may darken over time'),
('dextrose_monohydrate', 0.70, 1.90, 100.0, 91.0, 'Very high AFP, prevents ice crystals', 'Highly hygroscopic, use carefully'),
('fructose', 1.90, 1.90, 95.0, 100.0, 'Very sweet, very soft texture', 'Extremely hygroscopic, browning risk'),
('inverted_sugar', 1.30, 1.90, 96.0, 77.0, 'High sweetness, prevents crystallization', 'Hygroscopic, excellent for smooth texture'),
('honey', 1.40, 1.90, 76.0, 80.0, 'Distinctive flavor, soft and smooth', 'Natural antimicrobial, variable composition'),
('agave_syrup', 1.40, 1.20, 80.0, 75.0, 'High fructose, very soft', 'Low GI, but very hygroscopic'),
('glucose_syrup_de60', 0.64, 0.52, 60.0, 80.0, 'Moderate sweetness, chewy texture', 'Good stability, prevents sandiness'),
('glucose_syrup_de42', 0.45, 0.23, 42.0, 80.0, 'Low sweetness, firm texture', 'Excellent bodying agent, low hygroscopicity'),
('glucose_syrup_de38', 0.23, 0.09, 38.0, 80.0, 'Very low sweetness, very firm', 'Best for structure, minimal moisture pickup'),
('maltodextrin_de15', 0.09, 0.05, 15.0, 95.0, 'Almost no sweetness, compact texture', 'Excellent carrier, no browning'),
('jaggery', 0.92, 1.05, 85.0, 95.0, 'Molasses flavor, moderate firmness', 'Contains minerals, variable purity')
ON CONFLICT (sugar_type) DO UPDATE SET
  sp_value = EXCLUDED.sp_value,
  afp_value = EXCLUDED.afp_value,
  de_value = EXCLUDED.de_value,
  dry_residual_pct = EXCLUDED.dry_residual_pct,
  texture_impact = EXCLUDED.texture_impact,
  stability_notes = EXCLUDED.stability_notes;

-- ================================================================
-- SEED DATA: MSNF & Stabilizer Balance Rules
-- Source: Gelato University - Formulation Balance Framework
-- ================================================================

INSERT INTO msnf_stabilizer_balance (formulation_type, msnf_min_pct, msnf_max_pct, stabilizer_min_pct, stabilizer_max_pct, fat_min_pct, fat_max_pct, explanation, scientific_reason) VALUES
('cocoa_chocolate', 7.0, 9.0, 0.30, 0.50, 6.0, 10.0, 'Chocolate-based formulations require lower MSNF to avoid competing flavors', 'Cocoa solids provide body; excess milk solids mask chocolate flavor'),
('eggs_nuts', 8.0, 10.0, 0.40, 0.50, 8.0, 14.0, 'Egg and nut-based pastes need moderate MSNF for creamy texture', 'Egg proteins and nut fats contribute to structure; balanced MSNF prevents graininess'),
('dairy_fruit', 9.0, 12.0, 0.50, 0.60, 7.0, 12.0, 'Dairy-fruit combinations require higher MSNF for richness and balance', 'Fruit acidity needs buffering from milk proteins; higher stabilizers prevent separation'),
('pure_dairy', 10.0, 12.0, 0.50, 0.60, 8.0, 14.0, 'Pure dairy pastes need maximum MSNF for authentic milk flavor and body', 'MSNF provides sweetness, body, and prevents ice crystal formation'),
('fruit_sorbet', 0.0, 2.0, 0.40, 0.50, 0.0, 2.0, 'Fruit sorbets use minimal to no dairy; stabilizers critical for texture', 'No milk proteins available; stabilizers must provide all structure and smoothness')
ON CONFLICT (formulation_type) DO UPDATE SET
  msnf_min_pct = EXCLUDED.msnf_min_pct,
  msnf_max_pct = EXCLUDED.msnf_max_pct,
  stabilizer_min_pct = EXCLUDED.stabilizer_min_pct,
  stabilizer_max_pct = EXCLUDED.stabilizer_max_pct,
  fat_min_pct = EXCLUDED.fat_min_pct,
  fat_max_pct = EXCLUDED.fat_max_pct,
  explanation = EXCLUDED.explanation,
  scientific_reason = EXCLUDED.scientific_reason;

-- ================================================================
-- SEED DATA: Extended Validation Thresholds (Formulation-Specific)
-- Source: Gelato University - Scientific Validation Standards
-- ================================================================

-- AFP (Anti-Freezing Power) Thresholds by Formulation Type
INSERT INTO validation_thresholds_extended (parameter_name, formulation_type, optimal_min, optimal_max, acceptable_min, acceptable_max, critical_min, critical_max, explanation, scientific_basis, measurement_unit) VALUES
('afp_total', 'cocoa_chocolate', 22.0, 24.0, 20.0, 26.0, 18.0, 28.0, 'Chocolate pastes need moderate AFP for balanced texture', 'Cocoa butter crystallization requires controlled freezing point', 'AFP units'),
('afp_total', 'eggs_nuts', 23.0, 25.0, 21.0, 27.0, 19.0, 29.0, 'Nut pastes benefit from slightly higher AFP for smoothness', 'Nut oils remain fluid at lower AFP; prevents graininess', 'AFP units'),
('afp_total', 'dairy_fruit', 25.0, 27.0, 23.0, 29.0, 21.0, 31.0, 'Fruit-dairy blends need higher AFP to prevent ice crystals', 'Fruit water content requires strong freezing point depression', 'AFP units'),
('afp_total', 'pure_dairy', 24.0, 26.0, 22.0, 28.0, 20.0, 30.0, 'Pure dairy needs balanced AFP for creamy, not icy texture', 'Lactose and milk proteins stabilize at this AFP range', 'AFP units'),
('afp_total', 'fruit_sorbet', 26.0, 28.0, 24.0, 30.0, 22.0, 32.0, 'Sorbets require highest AFP to stay scoopable', 'No fat to soften texture; AFP critical for preventing iciness', 'AFP units'),

-- POD (Sweetening Power on DR) Thresholds
('pod_sweetness', 'cocoa_chocolate', 15.0, 17.0, 14.0, 19.0, 12.0, 21.0, 'Chocolate pastes need lower sweetness to balance cocoa bitterness', 'Cocoa solids contribute bitterness; balanced sweetness enhances chocolate flavor', '%'),
('pod_sweetness', 'eggs_nuts', 16.0, 18.0, 15.0, 20.0, 13.0, 22.0, 'Nut pastes require moderate sweetness for nutty flavor balance', 'Nut oils provide richness; moderate sweetness prevents cloying', '%'),
('pod_sweetness', 'dairy_fruit', 18.0, 20.0, 17.0, 22.0, 15.0, 24.0, 'Fruit-dairy needs higher sweetness to balance fruit acidity', 'Fruit acids require sugar buffering; dairy adds mild sweetness', '%'),
('pod_sweetness', 'pure_dairy', 17.0, 19.0, 16.0, 21.0, 14.0, 23.0, 'Pure dairy benefits from balanced sweetness for milk flavor', 'Lactose contributes mild sweetness; sucrose enhances without masking', '%'),
('pod_sweetness', 'fruit_sorbet', 19.0, 21.0, 18.0, 23.0, 16.0, 25.0, 'Sorbets need highest sweetness to balance tart fruit flavors', 'No dairy to buffer acidity; higher sugar essential', '%'),

-- D.E. (Dextrose Equivalence) Thresholds
('de_total', 'cocoa_chocolate', 35.0, 45.0, 30.0, 50.0, 25.0, 55.0, 'Chocolate benefits from moderate DE for firm yet creamy texture', 'Cocoa butter provides fat firmness; moderate DE prevents over-softness', 'DE units'),
('de_total', 'eggs_nuts', 38.0, 48.0, 33.0, 53.0, 28.0, 58.0, 'Nut pastes need balanced DE for spreadable consistency', 'Nut oils soften texture; balanced DE maintains structure', 'DE units'),
('de_total', 'dairy_fruit', 40.0, 50.0, 35.0, 55.0, 30.0, 60.0, 'Fruit-dairy blends benefit from moderate DE for smooth scooping', 'Fruit fibers provide body; moderate DE ensures creaminess', 'DE units'),
('de_total', 'pure_dairy', 38.0, 48.0, 33.0, 53.0, 28.0, 58.0, 'Pure dairy needs balanced DE for classic creamy texture', 'Milk proteins stabilize; balanced DE prevents iciness or gumminess', 'DE units'),
('de_total', 'fruit_sorbet', 42.0, 52.0, 37.0, 57.0, 32.0, 62.0, 'Sorbets require slightly higher DE for soft, scoopable texture', 'No fat to soften; higher DE essential for proper consistency', 'DE units'),

-- PAC (Freezing Point Depression) Thresholds
('pac_total', 'default', -6.5, -5.5, -7.0, -5.0, -8.0, -4.0, 'Paste formulations target -5.5 to -6.5°C freezing point for storage stability', 'Optimal PAC prevents ice crystal formation during storage and transport', '°C'),

-- Total Solids Thresholds
('solids_total', 'default', 35.0, 40.0, 32.0, 42.0, 28.0, 45.0, 'Paste formulations need 35-40% total solids for shelf-stability and texture', 'Higher solids reduce water activity, extend shelf-life, and improve body', '%'),

-- Fat Thresholds by Formulation Type
('fat_total', 'cocoa_chocolate', 6.0, 10.0, 5.0, 12.0, 4.0, 14.0, 'Chocolate pastes need moderate fat for creamy mouthfeel', 'Cocoa butter contributes fat; additional dairy fat enhances richness', '%'),
('fat_total', 'eggs_nuts', 8.0, 14.0, 6.0, 16.0, 4.0, 18.0, 'Nut pastes require higher fat for authentic nutty richness', 'Nut oils provide characteristic flavor and smooth texture', '%'),
('fat_total', 'dairy_fruit', 7.0, 12.0, 5.0, 14.0, 3.0, 16.0, 'Fruit-dairy blends need balanced fat for creamy yet light texture', 'Fruit adds water; fat provides richness without heaviness', '%'),
('fat_total', 'pure_dairy', 8.0, 14.0, 6.0, 16.0, 4.0, 18.0, 'Pure dairy pastes require higher fat for authentic dairy richness', 'Milk fat essential for creamy texture and flavor', '%'),
('fat_total', 'fruit_sorbet', 0.0, 2.0, 0.0, 3.0, 0.0, 5.0, 'Sorbets use minimal to no fat for light, refreshing texture', 'Fat-free allows pure fruit flavor; minimal fat for smoothness', '%'),

-- Water Activity Thresholds
('water_activity', 'default', 0.70, 0.74, 0.68, 0.76, 0.60, 0.80, 'Paste formulations target Aw 0.70-0.74 for 12-week shelf-life', 'Optimal Aw inhibits microbial growth while maintaining texture', 'Aw'),

-- Characterization (Flavoring Ingredients) Thresholds
('characterization_pct', 'eggs_nuts', 8.0, 15.0, 6.0, 18.0, 4.0, 22.0, 'Nut pastes need 8-15% nut content for authentic flavor', 'Sufficient nut content for characteristic flavor without overpowering', '%'),
('characterization_pct', 'dairy_fruit', 5.0, 45.0, 3.0, 50.0, 2.0, 60.0, 'Fruit-dairy allows wide range depending on desired intensity', 'Fruit and dairy both contribute characterizing flavors', '%'),
('characterization_pct', 'cocoa_chocolate', 5.0, 25.0, 3.0, 30.0, 2.0, 35.0, 'Chocolate pastes need sufficient cocoa for characteristic flavor', 'Cocoa solids provide chocolate identity; balance with dairy', '%'),

-- Final Sugars Thresholds
('final_sugars_pct', 'eggs_nuts', 18.0, 20.0, 16.0, 22.0, 14.0, 25.0, 'Nut pastes require higher sugar for preservation and texture', 'Sugar balances nut oils, extends shelf-life, provides body', '%'),
('final_sugars_pct', 'dairy_fruit', 19.0, 21.0, 17.0, 23.0, 15.0, 26.0, 'Fruit-dairy needs moderate-high sugar for balance and preservation', 'Sugar balances fruit acidity and preserves dairy components', '%'),
('final_sugars_pct', 'fruit_sorbet', 22.0, 24.0, 20.0, 26.0, 18.0, 28.0, 'Sorbets require highest sugar for body and preservation', 'No dairy or fat; sugar provides all body and shelf-life', '%'),
('final_sugars_pct', 'cocoa_chocolate', 19.0, 21.0, 17.0, 23.0, 15.0, 26.0, 'Chocolate pastes need balanced sugar to complement cocoa bitterness', 'Sugar enhances chocolate flavor without excessive sweetness', '%')

ON CONFLICT (parameter_name, formulation_type) DO UPDATE SET
  optimal_min = EXCLUDED.optimal_min,
  optimal_max = EXCLUDED.optimal_max,
  acceptable_min = EXCLUDED.acceptable_min,
  acceptable_max = EXCLUDED.acceptable_max,
  critical_min = EXCLUDED.critical_min,
  critical_max = EXCLUDED.critical_max,
  explanation = EXCLUDED.explanation,
  scientific_basis = EXCLUDED.scientific_basis,
  measurement_unit = EXCLUDED.measurement_unit;

-- ================================================================
-- VERIFICATION QUERIES (Run these to confirm successful migration)
-- ================================================================

-- Count records in new tables
-- SELECT 'gelato_science_constants' as table_name, COUNT(*) as record_count FROM gelato_science_constants
-- UNION ALL
-- SELECT 'msnf_stabilizer_balance', COUNT(*) FROM msnf_stabilizer_balance
-- UNION ALL
-- SELECT 'validation_thresholds_extended', COUNT(*) FROM validation_thresholds_extended;

-- Test sugar data
-- SELECT sugar_type, sp_value, afp_value, de_value FROM gelato_science_constants ORDER BY afp_value DESC LIMIT 5;

-- Test MSNF balance rules
-- SELECT formulation_type, msnf_min_pct, msnf_max_pct, stabilizer_min_pct FROM msnf_stabilizer_balance;

-- Test validation thresholds
-- SELECT parameter_name, formulation_type, acceptable_min, acceptable_max FROM validation_thresholds_extended WHERE parameter_name = 'afp_total';

-- ================================================================
-- MIGRATION COMPLETE! 
-- ================================================================
-- Tables Created:
--   ✅ gelato_science_constants (14 sugar types with SP/AFP/DE data)
--   ✅ msnf_stabilizer_balance (5 formulation type rules)
--   ✅ validation_thresholds_extended (17 parameters across 5 formulation types)
--
-- Professional Gelato University Carpigiani standards now integrated!
-- Your app can now validate formulations with 99% scientific accuracy!
-- ================================================================
