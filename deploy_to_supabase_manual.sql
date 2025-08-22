-- =============================================
-- MANUAL DEPLOYMENT SCRIPT FOR SUPABASE SQL EDITOR
-- Copy and paste this into your Supabase Dashboard > SQL Editor
-- =============================================

-- Step 1: Create the tables
CREATE TABLE IF NOT EXISTS historical_daily_sales (
    id BIGSERIAL PRIMARY KEY,
    store_name TEXT NOT NULL,
    sale_date DATE NOT NULL,
    day_of_week TEXT,
    day_number INTEGER,
    fiscal_year INTEGER NOT NULL,
    sales_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    data_type TEXT NOT NULL DEFAULT 'actual',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(store_name, sale_date, fiscal_year, data_type)
);

CREATE TABLE IF NOT EXISTS budget_forecasts (
    id BIGSERIAL PRIMARY KEY,
    store_name TEXT NOT NULL,
    forecast_date DATE NOT NULL,
    day_of_week TEXT,
    day_number INTEGER,
    fiscal_year INTEGER NOT NULL,
    forecast_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    forecast_type TEXT DEFAULT 'daily',
    variance_adjustment DECIMAL(5,4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(store_name, forecast_date, fiscal_year, forecast_type)
);

CREATE TABLE IF NOT EXISTS store_name_mapping (
    id SERIAL PRIMARY KEY,
    excel_store_name TEXT UNIQUE NOT NULL,
    database_store_name TEXT,
    store_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 2: Create indexes
CREATE INDEX IF NOT EXISTS idx_historical_sales_store_date ON historical_daily_sales(store_name, sale_date);
CREATE INDEX IF NOT EXISTS idx_historical_sales_fiscal_year ON historical_daily_sales(fiscal_year, data_type);
CREATE INDEX IF NOT EXISTS idx_budget_forecasts_store_date ON budget_forecasts(store_name, forecast_date);
CREATE INDEX IF NOT EXISTS idx_budget_forecasts_fiscal_year ON budget_forecasts(fiscal_year, forecast_type);

-- Step 3: Create the main view
CREATE OR REPLACE VIEW daily_sales_budget_view AS
SELECT 
    hds.store_name,
    snm.store_id,
    hds.sale_date,
    hds.day_of_week,
    hds.fiscal_year,
    hds.sales_amount as actual_sales,
    bf.forecast_amount as budget_forecast,
    CASE 
        WHEN bf.forecast_amount > 0 AND hds.sales_amount > 0 
        THEN ((hds.sales_amount - bf.forecast_amount) / bf.forecast_amount) * 100
        ELSE NULL 
    END as variance_percent,
    hds.sales_amount - COALESCE(bf.forecast_amount, 0) as variance_amount,
    hds.data_type,
    hds.created_at
FROM historical_daily_sales hds
LEFT JOIN budget_forecasts bf 
    ON hds.store_name = bf.store_name 
    AND hds.sale_date = bf.forecast_date 
    AND hds.fiscal_year = bf.fiscal_year
LEFT JOIN store_name_mapping snm 
    ON hds.store_name = snm.excel_store_name
WHERE hds.data_type = 'actual';

-- Step 4: Insert store mappings
INSERT INTO store_name_mapping (excel_store_name, database_store_name) VALUES
('Colwood', 'Cascadia Hatley Park'),
('Quadra', 'Cascadia Quadra Village'),
('Crown', 'Cascadia Courtenay (Crown Isle)'),
('Uptown', 'Cascadia Uptown'),
('Langford', 'Cascadia Langford'),
('Eagle Creek', 'Cascadia Eagle Creek'),
('Nanoose', 'Cascadia Nanoose Bay'),
('Parksville', 'Cascadia Parksville'),
('Caddy Bay', 'Cascadia Caddy Bay'),
('Port A', 'Cascadia Port Alberni'),
('Royal B', 'Cascadia Royal Bay'),
('Allandale', 'Cascadia Allandale'),
('Bear', 'Bear Mountain')
ON CONFLICT (excel_store_name) DO NOTHING;

-- Step 5: Update store mappings with actual store_ids
UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Quadra Village')
WHERE excel_store_name = 'Quadra';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Courtenay (Crown Isle)')
WHERE excel_store_name = 'Crown';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Uptown')
WHERE excel_store_name = 'Uptown';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Langford')
WHERE excel_store_name = 'Langford';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Eagle Creek')
WHERE excel_store_name = 'Eagle Creek';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Nanoose Bay')
WHERE excel_store_name = 'Nanoose';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Parksville')
WHERE excel_store_name = 'Parksville';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Caddy Bay')
WHERE excel_store_name = 'Caddy Bay';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Port Alberni')
WHERE excel_store_name = 'Port A';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Royal Bay')
WHERE excel_store_name = 'Royal B';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Allandale')
WHERE excel_store_name = 'Allandale';

UPDATE store_name_mapping 
SET store_id = (SELECT store_id FROM store WHERE name = 'Cascadia Hatley Park')
WHERE excel_store_name = 'Colwood';

-- Step 6: Verify the setup
SELECT 'Tables created' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('historical_daily_sales', 'budget_forecasts', 'store_name_mapping');

SELECT 'Store mappings' as status;
SELECT excel_store_name, store_id, database_store_name 
FROM store_name_mapping 
ORDER BY excel_store_name;