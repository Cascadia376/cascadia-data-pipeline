-- =============================================
-- Historical Sales and Budget Data Schema
-- For Cascadia Daily Sales & Budget Data integration
-- =============================================

-- Create tables for historical sales and budget data
CREATE TABLE IF NOT EXISTS historical_daily_sales (
    id BIGSERIAL PRIMARY KEY,
    store_name TEXT NOT NULL,
    sale_date DATE NOT NULL,
    day_of_week TEXT,
    day_number INTEGER, -- 1-7 (Sunday = 1)
    fiscal_year INTEGER NOT NULL,
    sales_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    data_type TEXT NOT NULL DEFAULT 'actual', -- 'actual' or 'forecast'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(store_name, sale_date, fiscal_year, data_type)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_historical_sales_store_date ON historical_daily_sales(store_name, sale_date);
CREATE INDEX IF NOT EXISTS idx_historical_sales_fiscal_year ON historical_daily_sales(fiscal_year, data_type);
CREATE INDEX IF NOT EXISTS idx_historical_sales_date_range ON historical_daily_sales(sale_date, data_type);

-- Budget/Forecast data table
CREATE TABLE IF NOT EXISTS budget_forecasts (
    id BIGSERIAL PRIMARY KEY,
    store_name TEXT NOT NULL,
    forecast_date DATE NOT NULL,
    day_of_week TEXT,
    day_number INTEGER, -- 1-7 (Sunday = 1)
    fiscal_year INTEGER NOT NULL,
    forecast_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    forecast_type TEXT DEFAULT 'daily', -- 'daily', 'weekly', 'monthly', 'annual'
    variance_adjustment DECIMAL(5,4) DEFAULT 0, -- Adjustment factor (-0.05 = -5%)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(store_name, forecast_date, fiscal_year, forecast_type)
);

-- Create indexes for budget forecasts
CREATE INDEX IF NOT EXISTS idx_budget_forecasts_store_date ON budget_forecasts(store_name, forecast_date);
CREATE INDEX IF NOT EXISTS idx_budget_forecasts_fiscal_year ON budget_forecasts(fiscal_year, forecast_type);
CREATE INDEX IF NOT EXISTS idx_budget_forecasts_date_range ON budget_forecasts(forecast_date, forecast_type);

-- Store mapping table to handle Excel store names to database store_id mapping
CREATE TABLE IF NOT EXISTS store_name_mapping (
    id SERIAL PRIMARY KEY,
    excel_store_name TEXT UNIQUE NOT NULL,
    database_store_name TEXT,
    store_id INTEGER REFERENCES store(store_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert store mappings based on Excel headers and existing store data
INSERT INTO store_name_mapping (excel_store_name, database_store_name) VALUES
('Colwood', 'Cascadia Hatley Park'), -- Assuming Colwood maps to Hatley Park
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
('Bear', 'Bear Mountain') -- New store not in current system
ON CONFLICT (excel_store_name) DO NOTHING;

-- =============================================
-- Views for Dashboard Integration
-- =============================================

-- Combined sales and budget view for dashboard
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

-- Monthly aggregated view
CREATE OR REPLACE VIEW monthly_sales_budget_summary AS
SELECT 
    store_name,
    store_id,
    DATE_TRUNC('month', sale_date) as month_year,
    fiscal_year,
    COUNT(*) as days_in_month,
    SUM(actual_sales) as total_actual_sales,
    SUM(budget_forecast) as total_budget_forecast,
    AVG(variance_percent) as avg_variance_percent,
    SUM(variance_amount) as total_variance_amount,
    CASE 
        WHEN SUM(budget_forecast) > 0 
        THEN ((SUM(actual_sales) - SUM(budget_forecast)) / SUM(budget_forecast)) * 100
        ELSE NULL 
    END as month_variance_percent
FROM daily_sales_budget_view
GROUP BY store_name, store_id, DATE_TRUNC('month', sale_date), fiscal_year
ORDER BY month_year DESC;

-- Weekly aggregated view
CREATE OR REPLACE VIEW weekly_sales_budget_summary AS
SELECT 
    store_name,
    store_id,
    DATE_TRUNC('week', sale_date) as week_starting,
    fiscal_year,
    COUNT(*) as days_in_week,
    SUM(actual_sales) as total_actual_sales,
    SUM(budget_forecast) as total_budget_forecast,
    AVG(variance_percent) as avg_variance_percent,
    SUM(variance_amount) as total_variance_amount,
    CASE 
        WHEN SUM(budget_forecast) > 0 
        THEN ((SUM(actual_sales) - SUM(budget_forecast)) / SUM(budget_forecast)) * 100
        ELSE NULL 
    END as week_variance_percent
FROM daily_sales_budget_view
GROUP BY store_name, store_id, DATE_TRUNC('week', sale_date), fiscal_year
ORDER BY week_starting DESC;

-- =============================================
-- Functions for Data Import and Processing
-- =============================================

-- Function to import daily sales data from Excel structure
CREATE OR REPLACE FUNCTION import_daily_sales_data(
    p_store_name TEXT,
    p_sale_date DATE,
    p_day_of_week TEXT,
    p_day_number INTEGER,
    p_fiscal_year INTEGER,
    p_sales_amount DECIMAL,
    p_data_type TEXT DEFAULT 'actual'
) RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO historical_daily_sales (
        store_name, sale_date, day_of_week, day_number, 
        fiscal_year, sales_amount, data_type
    ) VALUES (
        p_store_name, p_sale_date, p_day_of_week, p_day_number,
        p_fiscal_year, p_sales_amount, p_data_type
    )
    ON CONFLICT (store_name, sale_date, fiscal_year, data_type) 
    DO UPDATE SET
        sales_amount = EXCLUDED.sales_amount,
        day_of_week = EXCLUDED.day_of_week,
        day_number = EXCLUDED.day_number,
        updated_at = NOW();
    
    RETURN TRUE;
EXCEPTION 
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Function to import budget forecast data
CREATE OR REPLACE FUNCTION import_budget_forecast_data(
    p_store_name TEXT,
    p_forecast_date DATE,
    p_day_of_week TEXT,
    p_day_number INTEGER,
    p_fiscal_year INTEGER,
    p_forecast_amount DECIMAL,
    p_variance_adjustment DECIMAL DEFAULT 0,
    p_forecast_type TEXT DEFAULT 'daily'
) RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO budget_forecasts (
        store_name, forecast_date, day_of_week, day_number,
        fiscal_year, forecast_amount, variance_adjustment, forecast_type
    ) VALUES (
        p_store_name, p_forecast_date, p_day_of_week, p_day_number,
        p_fiscal_year, p_forecast_amount, p_variance_adjustment, p_forecast_type
    )
    ON CONFLICT (store_name, forecast_date, fiscal_year, forecast_type)
    DO UPDATE SET
        forecast_amount = EXCLUDED.forecast_amount,
        variance_adjustment = EXCLUDED.variance_adjustment,
        day_of_week = EXCLUDED.day_of_week,
        day_number = EXCLUDED.day_number,
        updated_at = NOW();
    
    RETURN TRUE;
EXCEPTION 
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- Trigger for updated_at timestamps
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_historical_sales_updated_at
    BEFORE UPDATE ON historical_daily_sales
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budget_forecasts_updated_at
    BEFORE UPDATE ON budget_forecasts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- Comments for documentation
-- =============================================
COMMENT ON TABLE historical_daily_sales IS 'Historical daily sales data imported from Excel files including both actual and forecast data';
COMMENT ON TABLE budget_forecasts IS 'Budget and forecast data by store and date for variance analysis';
COMMENT ON TABLE store_name_mapping IS 'Mapping between Excel store names and database store records';
COMMENT ON VIEW daily_sales_budget_view IS 'Combined view of daily sales actuals vs budget with variance calculations';
COMMENT ON VIEW monthly_sales_budget_summary IS 'Monthly aggregated sales vs budget performance';
COMMENT ON VIEW weekly_sales_budget_summary IS 'Weekly aggregated sales vs budget performance';