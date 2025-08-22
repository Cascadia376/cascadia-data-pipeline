#!/usr/bin/env python3
"""
Test database connection before running full import
"""
import os
import psycopg2
from dotenv import load_dotenv

def test_connection():
    """Test if we can connect to the database"""
    
    # Load environment variables
    load_dotenv()
    
    connection_string = os.getenv('DATABASE_URL')
    if not connection_string:
        print("ERROR: DATABASE_URL not found in .env file")
        print("Please update the .env file with your Supabase database connection string")
        return False
    
    if '[YOUR_DB_PASSWORD]' in connection_string:
        print("ERROR: Please replace [YOUR_DB_PASSWORD] in .env file with your actual database password")
        print("You can find this in: Supabase Dashboard > Settings > Database")
        return False
    
    try:
        print("Testing database connection...")
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print("SUCCESS: Connected successfully!")
        print(f"PostgreSQL version: {version}")
        
        # Test if our tables exist (from Phase 1)
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('historical_daily_sales', 'budget_forecasts', 'store_name_mapping')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if len(tables) == 3:
            print("SUCCESS: Budget integration tables found - ready for data import!")
        elif len(tables) > 0:
            print(f"WARNING: Only found {len(tables)} tables: {tables}")
            print("You may need to run Phase 1 deployment first")
        else:
            print("ERROR: No budget integration tables found")
            print("Please run Phase 1 deployment first")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        print("\nPlease check:")
        print("1. Your DATABASE_URL is correct")
        print("2. Your database password is correct")
        print("3. Your network allows connections to Supabase")
        return False

if __name__ == "__main__":
    print("Testing Supabase database connection...")
    print("=" * 50)
    success = test_connection()
    print("=" * 50)
    if success:
        print("SUCCESS: Ready to proceed with Excel data import!")
    else:
        print("ERROR: Please fix connection issues first")