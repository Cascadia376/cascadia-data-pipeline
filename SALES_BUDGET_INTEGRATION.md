# Sales & Budget Data Integration

This document outlines the integration of historical sales data and budget forecasts from the Excel file "Cascadia Daily Sales & Budget Data.xlsx" into the database and dashboard system.

## Overview

The integration adds real budget and variance tracking capabilities to the dashboard by:

1. **Database Schema**: New tables for historical sales and budget data
2. **Data Import**: Python scripts to parse and import Excel data
3. **API Integration**: Supabase functions to serve data to the dashboard
4. **Dashboard Updates**: Enhanced data service with real budget data

## Files Created/Modified

### Database Schema
- `sales_budget_schema.sql` - Complete database schema for sales and budget data
- `deploy_phase3_schema.sql` - May need to include the new schema

### Data Import Scripts
- `import_sales_budget_data.py` - Main import script for Excel data
- `setup_sales_budget_system.py` - Complete setup script for the entire system

### Dashboard Integration
- `supabase/functions/sales-budget-data/index.ts` - New Supabase function
- `src/lib/dataService.ts` - Updated with real budget data functions

## Database Schema

### New Tables

#### `historical_daily_sales`
Stores daily sales data (both actual and forecast):
- `store_name`, `sale_date`, `fiscal_year`
- `sales_amount`, `data_type` (actual/forecast)
- `day_of_week`, `day_number`

#### `budget_forecasts`
Stores budget and forecast data:
- `store_name`, `forecast_date`, `fiscal_year`
- `forecast_amount`, `variance_adjustment`
- `forecast_type` (daily/weekly/monthly)

#### `store_name_mapping`
Maps Excel store names to database store IDs:
- `excel_store_name` → `store_id`
- Handles name differences between Excel and database

### Views Created

#### `daily_sales_budget_view`
Combined view showing actual vs budget with variance calculations:
```sql
SELECT store_name, sale_date, actual_sales, budget_forecast, 
       variance_percent, variance_amount
FROM daily_sales_budget_view
WHERE store_id = 1 AND sale_date >= '2024-01-01'
```

#### `monthly_sales_budget_summary`
Monthly aggregated performance:
```sql
SELECT store_name, month_year, total_actual_sales, total_budget_forecast,
       month_variance_percent
FROM monthly_sales_budget_summary
WHERE store_id = 1
ORDER BY month_year DESC
```

## Excel Data Structure

The Excel file contains:
- **Row 0**: Store headers (Colwood, Quadra, Crown, Uptown, etc.)
- **Row 1**: Variance adjustment factors (-0.05, 0.015, etc.)
- **Row 2**: Structure indicators (FY25, FY26, FCST)
- **Row 3+**: Daily data with dates and sales amounts

### Store Mapping
| Excel Name | Database Store Name |
|------------|-------------------|
| Colwood | Cascadia Hatley Park |
| Quadra | Cascadia Quadra Village |
| Crown | Cascadia Courtenay (Crown Isle) |
| Uptown | Cascadia Uptown |
| Langford | Cascadia Langford |
| Eagle Creek | Cascadia Eagle Creek |
| Nanoose | Cascadia Nanoose Bay |
| Parksville | Cascadia Parksville |
| Caddy Bay | Cascadia Caddy Bay |
| Port A | Cascadia Port Alberni |
| Royal B | Cascadia Royal Bay |
| Allandale | Cascadia Allandale |
| Bear | Bear Mountain (new store) |

## Setup Instructions

### Prerequisites
1. Python 3.8+ with pandas, psycopg2
2. Access to Supabase database
3. Excel file in the specified location

### 1. Database Setup
```bash
# Set your database connection string
export DATABASE_URL="postgresql://postgres:[password]@[host]:5432/postgres"

# Run the complete setup
python setup_sales_budget_system.py
```

This will:
- Deploy the database schema
- Update store mappings
- Import all Excel data
- Verify the setup

### 2. Deploy Supabase Function
```bash
# From the dashboard directory
cd C:\Users\Jay\OneDrive - trufflesgroupttg\chain-flow-metrics-19

# Deploy the new function
supabase functions deploy sales-budget-data
```

### 3. Test Dashboard Integration
The dashboard will automatically use real budget data when available, falling back to mock data if not.

## API Usage

### Supabase Function: `sales-budget-data`

#### Request Parameters
```json
{
  "storeId": 1,
  "timeFrame": "monthly",
  "dataType": "combined",
  "startDate": "2024-01-01",
  "endDate": "2024-12-31"
}
```

#### Response Formats

**Combined Data (`dataType: "combined"`)**:
```json
[
  {
    "period": "2024-01-01",
    "store_name": "Cascadia Quadra Village",
    "store_id": 1,
    "actual_sales": 15420.50,
    "budget_forecast": 16000.00,
    "variance_amount": -579.50,
    "variance_percent": -3.62,
    "fiscal_year": 2024
  }
]
```

**Budget Only (`dataType: "budget_only"`)**:
```json
[
  {
    "period": "2024-01-01",
    "store_name": "Cascadia Quadra Village", 
    "budget": 16000.00,
    "fiscal_year": 2024
  }
]
```

**Variance Only (`dataType: "variance_only"`)**:
```json
[
  {
    "period": "2024-01-01",
    "variance_amount": -579.50,
    "variance_percent": -3.62,
    "fiscal_year": 2024
  }
]
```

## Dashboard Functions

### Updated Functions in `dataService.ts`

#### `fetchRevenueTrends(timeFrame, storeId)`
Now fetches real budget data and includes variance information:
```typescript
const data = await fetchRevenueTrends('monthly', 1);
// Returns: { period, current, budget, lastYear, variance_amount, variance_percent }
```

#### `fetchBudgetVariance(storeId, timeFrame, startDate?, endDate?)`
Dedicated function for variance analysis:
```typescript
const variance = await fetchBudgetVariance(1, 'monthly', '2024-01-01', '2024-12-31');
```

#### `fetchBudgetComparison(storeId, timeFrame)`
Comparison of actual vs budget:
```typescript
const comparison = await fetchBudgetComparison(1, 'monthly');
// Returns: { period, actual, budget, variance_percent, variance_amount, store_name }
```

## Data Import Process

### Manual Import
```bash
python import_sales_budget_data.py
```

### Automated Import
The import script can be scheduled to run regularly if the Excel file is updated:
```bash
# Add to cron or task scheduler
0 6 * * * /path/to/python import_sales_budget_data.py
```

## Verification Queries

### Check Data Import
```sql
-- Verify historical data
SELECT store_name, COUNT(*), MIN(sale_date), MAX(sale_date)
FROM historical_daily_sales 
GROUP BY store_name;

-- Verify budget data  
SELECT store_name, COUNT(*), MIN(forecast_date), MAX(forecast_date)
FROM budget_forecasts
GROUP BY store_name;

-- Check variance calculations
SELECT store_name, 
       COUNT(*) as total_days,
       AVG(variance_percent) as avg_variance_pct,
       SUM(variance_amount) as total_variance
FROM daily_sales_budget_view
WHERE sale_date >= '2024-01-01'
GROUP BY store_name;
```

### Performance Test
```sql
-- Test aggregation performance
SELECT store_name,
       DATE_TRUNC('month', sale_date) as month,
       SUM(actual_sales) as monthly_sales,
       SUM(budget_forecast) as monthly_budget
FROM daily_sales_budget_view
WHERE sale_date >= '2024-01-01'
GROUP BY store_name, DATE_TRUNC('month', sale_date)
ORDER BY month DESC;
```

## Troubleshooting

### Common Issues

1. **Import Fails**: Check Excel file path and format
2. **No Budget Data in Dashboard**: Verify Supabase function deployment
3. **Store Mapping Issues**: Check store_name_mapping table
4. **Date Format Problems**: Ensure Excel dates are properly formatted

### Debug Queries
```sql
-- Check store mappings
SELECT * FROM store_name_mapping WHERE store_id IS NOT NULL;

-- Check recent imports
SELECT store_name, MAX(created_at) as last_import
FROM historical_daily_sales
GROUP BY store_name;

-- Verify function accessibility
SELECT * FROM daily_sales_budget_view LIMIT 5;
```

## Future Enhancements

1. **Historical Comparison**: Add previous year actual data
2. **Forecast Accuracy**: Track forecast vs actual performance
3. **Automated Imports**: Set up automatic Excel file processing
4. **Advanced Analytics**: Add seasonal adjustments and trending
5. **Alert System**: Budget variance threshold notifications

## Maintenance

### Regular Tasks
1. Monitor import logs for errors
2. Update store mappings when new stores are added
3. Archive old data periodically
4. Review variance calculation accuracy

### Data Quality Checks
1. Daily data completeness
2. Reasonable variance ranges
3. Date continuity
4. Store mapping accuracy

---

**Last Updated**: August 2025  
**Version**: 1.0  
**Contact**: Development Team