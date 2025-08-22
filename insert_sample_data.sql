-- =============================================
-- SAMPLE DATA FOR TESTING BUDGET INTEGRATION
-- Run this after the main deployment script
-- =============================================

-- Insert sample historical sales data (FY2025 - actual data)
INSERT INTO historical_daily_sales (store_name, sale_date, day_of_week, day_number, fiscal_year, sales_amount, data_type) VALUES
-- Quadra Village sample data
('Quadra', '2024-05-02', 'Thursday', 5, 2025, 16424.39, 'actual'),
('Quadra', '2024-05-03', 'Friday', 6, 2025, 26863.47, 'actual'),
('Quadra', '2024-05-04', 'Saturday', 7, 2025, 2440.61, 'actual'),
('Quadra', '2024-05-05', 'Sunday', 1, 2025, 2478.67, 'actual'),
('Quadra', '2024-05-06', 'Monday', 2, 2025, 7967.21, 'actual'),

-- Crown Isle sample data
('Crown', '2024-05-02', 'Thursday', 5, 2025, 33045.18, 'actual'),
('Crown', '2024-05-03', 'Friday', 6, 2025, 43251.57, 'actual'),
('Crown', '2024-05-04', 'Saturday', 7, 2025, 41701.21, 'actual'),
('Crown', '2024-05-05', 'Sunday', 1, 2025, 22282.61, 'actual'),
('Crown', '2024-05-06', 'Monday', 2, 2025, 26339.49, 'actual'),

-- Uptown sample data
('Uptown', '2024-05-02', 'Thursday', 5, 2025, 12046.68, 'actual'),
('Uptown', '2024-05-03', 'Friday', 6, 2025, 18431.69, 'actual'),
('Uptown', '2024-05-04', 'Saturday', 7, 2025, 18547.80, 'actual'),
('Uptown', '2024-05-05', 'Sunday', 1, 2025, 10921.16, 'actual'),
('Uptown', '2024-05-06', 'Monday', 2, 2025, 7514.16, 'actual')

ON CONFLICT (store_name, sale_date, fiscal_year, data_type) DO NOTHING;

-- Insert sample budget forecast data (FY2026 - forecast data)
INSERT INTO budget_forecasts (store_name, forecast_date, day_of_week, day_number, fiscal_year, forecast_amount, variance_adjustment, forecast_type) VALUES
-- Quadra Village forecasts
('Quadra', '2025-05-01', 'Thursday', 5, 2026, 15603.17, -0.05, 'daily'),
('Quadra', '2025-05-02', 'Friday', 6, 2026, 25520.30, -0.05, 'daily'),
('Quadra', '2025-05-03', 'Saturday', 7, 2026, 2318.58, -0.05, 'daily'),
('Quadra', '2025-05-04', 'Sunday', 1, 2026, 2354.74, -0.05, 'daily'),
('Quadra', '2025-05-05', 'Monday', 2, 2026, 7568.85, -0.05, 'daily'),

-- Crown Isle forecasts
('Crown', '2025-05-01', 'Thursday', 5, 2026, 33540.86, 0.015, 'daily'),
('Crown', '2025-05-02', 'Friday', 6, 2026, 43900.34, 0.015, 'daily'),
('Crown', '2025-05-03', 'Saturday', 7, 2026, 42326.73, 0.015, 'daily'),
('Crown', '2025-05-04', 'Sunday', 1, 2026, 22616.85, 0.015, 'daily'),
('Crown', '2025-05-05', 'Monday', 2, 2026, 26734.58, 0.015, 'daily'),

-- Uptown forecasts  
('Uptown', '2025-05-01', 'Thursday', 5, 2026, 12408.08, 0.03, 'daily'),
('Uptown', '2025-05-02', 'Friday', 6, 2026, 18984.64, 0.03, 'daily'),
('Uptown', '2025-05-03', 'Saturday', 7, 2026, 19104.23, 0.03, 'daily'),
('Uptown', '2025-05-04', 'Sunday', 1, 2026, 11248.79, 0.03, 'daily'),
('Uptown', '2025-05-05', 'Monday', 2, 2026, 7739.58, 0.03, 'daily')

ON CONFLICT (store_name, forecast_date, fiscal_year, forecast_type) DO NOTHING;

-- Verify the data was inserted
SELECT 'Sample data inserted successfully' as status;

SELECT 
    store_name,
    COUNT(*) as records,
    MIN(sale_date) as earliest_date,
    MAX(sale_date) as latest_date,
    SUM(sales_amount) as total_sales
FROM historical_daily_sales 
GROUP BY store_name 
ORDER BY store_name;

SELECT 
    store_name,
    COUNT(*) as forecast_records,
    MIN(forecast_date) as earliest_forecast,
    MAX(forecast_date) as latest_forecast,
    SUM(forecast_amount) as total_forecast
FROM budget_forecasts 
GROUP BY store_name 
ORDER BY store_name;

-- Test the budget view
SELECT 
    store_name,
    sale_date,
    actual_sales,
    budget_forecast,
    variance_amount,
    variance_percent
FROM daily_sales_budget_view 
WHERE store_name IN ('Quadra', 'Crown', 'Uptown')
ORDER BY store_name, sale_date
LIMIT 10;