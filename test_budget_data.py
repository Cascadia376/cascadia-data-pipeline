#!/usr/bin/env python3
"""
Quick test script to verify budget data is available
"""
import os
import psycopg2
from datetime import datetime

def test_budget_data():
    """Test if budget data is properly loaded"""
    
    connection_string = os.getenv('DATABASE_URL')
    if not connection_string:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Test 1: Check if tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('historical_daily_sales', 'budget_forecasts', 'store_name_mapping')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Found tables: {tables}")
        
        # Test 2: Check data counts
        cursor.execute("SELECT COUNT(*) FROM historical_daily_sales")
        historical_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM budget_forecasts") 
        forecast_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM store_name_mapping WHERE store_id IS NOT NULL")
        mapping_count = cursor.fetchone()[0]
        
        print(f"✅ Data counts:")
        print(f"   Historical sales: {historical_count}")
        print(f"   Budget forecasts: {forecast_count}")
        print(f"   Store mappings: {mapping_count}")
        
        # Test 3: Check sample budget view data
        cursor.execute("""
            SELECT store_name, COUNT(*) as records, 
                   MIN(sale_date) as earliest_date, 
                   MAX(sale_date) as latest_date,
                   SUM(actual_sales) as total_sales,
                   SUM(budget_forecast) as total_budget
            FROM daily_sales_budget_view 
            GROUP BY store_name 
            ORDER BY total_sales DESC 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        if results:
            print(f"✅ Sample budget data:")
            for row in results:
                store, records, earliest, latest, sales, budget = row
                print(f"   {store}: {records} records, ${sales:,.2f} sales, ${budget:,.2f} budget")
        else:
            print("⚠️  No budget view data found")
        
        cursor.close()
        conn.close()
        
        if historical_count > 0 and forecast_count > 0 and mapping_count > 0:
            print("✅ Budget data integration is working!")
            return True
        else:
            print("❌ Missing data - run setup_sales_budget_system.py")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing budget data integration...")
    print("=" * 50)
    success = test_budget_data()
    print("=" * 50)
    if success:
        print("🎉 Ready to deploy Supabase function!")
    else:
        print("🔧 Fix database issues first")