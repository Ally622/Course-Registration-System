-- Migration: Add duration_years column to programmes table
-- Run this if you already have a database without duration_years

ALTER TABLE programmes 
ADD COLUMN IF NOT EXISTS duration_years INT DEFAULT 4 
AFTER department_id;
