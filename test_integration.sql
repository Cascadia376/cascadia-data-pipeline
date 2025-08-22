-- =============================================
-- TEST BUDGET INTEGRATION
-- Run this in Supabase SQL Editor to verify everything works
-- =============================================

-- Test 1: Check if tables exist and have data
SELECT 'Tables and Data Status' as test_name;

SELECT 
    'historical_daily_sales' as table_name,
    COUNT(*) as record_count,
    MIN(sale_date) as earliest_date,
    MAX(sale_date) as latest_date
FROM historical_daily_sales
UNION ALL
SELECT 
    'budget_forecasts' as table_name,
    COUNT(*) as record_count,
    MIN(forecast_date::date) as earliest_date,
    MAX(forecast_date::date) as latest_date
FROM budget_forecasts
UNION ALL
SELECT 
    'store_name_mapping' as table_name,
    COUNT(*) as record_count,
    NULL as earliest_date,
    NULL as latest_date
FROM store_name_mapping;

-- Test 2: Check store mappings
SELECT 'Store Mappings' as test_name;
SELECT 
    excel_store_name,
    database_store_name,
    store_id,
    CASE WHEN store_id IS NOT NULL THEN 'Mapped' ELSE 'Not Mapped' END as status
FROM store_name_mapping
ORDER BY excel_store_name;

-- Test 3: Test the budget view (this is what the dashboard will use)
SELECT 'Budget View Test' as test_name;
SELECT 
    store_name,
    COUNT(*) as total_records,
    SUM(actual_sales) as total_actual_sales,
    SUM(budget_forecast) as total_budget_forecast,
    ROUND(AVG(variance_percent), 2) as avg_variance_percent
FROM daily_sales_budget_view
GROUP BY store_name
ORDER BY total_actual_sales DESC;

-- Test 4: Sample daily data (what dashboard charts will show)
SELECT 'Sample Daily Data' as test_name;
SELECT 
    store_name,
    sale_date,
    actual_sales,
    budget_forecast,
    variance_amount,
    ROUND(variance_percent, 2) as variance_percent
FROM daily_sales_budget_view
WHERE store_name IN ('Quadra', 'Crown', 'Uptown')
ORDER BY store_name, sale_date
LIMIT 15;

-- Test 5: Check if this data will replace the mock budget data
SELECT 'Budget Comparison Test' as test_name;
SELECT 
    store_name,
    actual_sales,
    budget_forecast,
    ROUND(actual_sales * 1.1, 2) as mock_budget_110_percent,
    CASE 
        WHEN budget_forecast = ROUND(actual_sales * 1.1, 2) THEN 'STILL USING MOCK DATA'
        WHEN budget_forecast IS NULL THEN 'NO BUDGET DATA'
        ELSE 'REAL BUDGET DATA ✓'
    END as budget_status
FROM daily_sales_budget_view
WHERE store_name = 'Quadra' AND sale_date = '2024-05-02';