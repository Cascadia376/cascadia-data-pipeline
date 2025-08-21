#!/usr/bin/env python3
"""
Setup script for the Sales & Budget Data system
This script will:
1. Deploy the database schema
2. Import the Excel data
3. Verify the setup
"""

import os
import sys
import psycopg2
import logging
from import_sales_budget_data import SalesBudgetImporter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sales_budget_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def deploy_schema(connection_string: str) -> bool:
    """Deploy the database schema"""
    try:
        logger.info("Deploying database schema...")
        
        # Read the schema SQL file
        schema_file = os.path.join(os.path.dirname(__file__), 'sales_budget_schema.sql')
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Connect and execute
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Execute the schema
        cursor.execute(schema_sql)
        conn.commit()
        
        logger.info("Database schema deployed successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to deploy schema: {e}")
        return False

def update_store_mappings(connection_string: str) -> bool:
    """Update store mappings with actual store_id values"""
    try:
        logger.info("Updating store mappings...")
        
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Get existing stores from the store table
        cursor.execute("SELECT store_id, name FROM store ORDER BY store_id")
        stores = cursor.fetchall()
        
        logger.info(f"Found {len(stores)} stores in database")
        for store_id, name in stores:
            logger.info(f"  {store_id}: {name}")
        
        # Update mappings where we can match names
        mapping_updates = [
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
            ('Colwood', 'Cascadia Hatley Park')  # Assuming Colwood maps to Hatley Park
        ]
        
        for excel_name, db_name in mapping_updates:
            cursor.execute("""
                UPDATE store_name_mapping 
                SET store_id = (SELECT store_id FROM store WHERE name = %s)
                WHERE excel_store_name = %s
            """, (db_name, excel_name))
            
            # Check if update was successful
            cursor.execute("""
                SELECT store_id FROM store_name_mapping 
                WHERE excel_store_name = %s
            """, (excel_name,))
            result = cursor.fetchone()
            
            if result and result[0]:
                logger.info(f"Mapped {excel_name} to store_id {result[0]} ({db_name})")
            else:
                logger.warning(f"Could not map {excel_name} to {db_name}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Store mappings updated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update store mappings: {e}")
        return False

def verify_setup(connection_string: str) -> bool:
    """Verify the setup was successful"""
    try:
        logger.info("Verifying setup...")
        
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('historical_daily_sales', 'budget_forecasts', 'store_name_mapping')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Found tables: {tables}")
        
        # Check data counts
        cursor.execute("SELECT COUNT(*) FROM historical_daily_sales")
        historical_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM budget_forecasts")
        forecast_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM store_name_mapping WHERE store_id IS NOT NULL")
        mapping_count = cursor.fetchone()[0]
        
        logger.info(f"Data counts:")
        logger.info(f"  Historical sales: {historical_count}")
        logger.info(f"  Budget forecasts: {forecast_count}")
        logger.info(f"  Store mappings: {mapping_count}")
        
        # Test the view
        cursor.execute("SELECT COUNT(*) FROM daily_sales_budget_view")
        view_count = cursor.fetchone()[0]
        logger.info(f"  Budget view records: {view_count}")
        
        cursor.close()
        conn.close()
        
        if historical_count > 0 and forecast_count > 0 and mapping_count > 0:
            logger.info("Setup verification successful!")
            return True
        else:
            logger.warning("Setup verification found issues with data counts")
            return False
        
    except Exception as e:
        logger.error(f"Setup verification failed: {e}")
        return False

def main():
    """Main setup process"""
    logger.info("Starting Sales & Budget Data system setup")
    
    # Configuration
    excel_file_path = r"C:\Users\Jay\OneDrive - trufflesgroupttg\Database Design & Planning Documents\Cascadia Daily Sales & Budget Data.xlsx"
    connection_string = os.getenv('DATABASE_URL')
    
    if not connection_string:
        logger.error("Please set DATABASE_URL environment variable with your Supabase connection string")
        logger.error("Example: postgresql://postgres:[password]@[host]:5432/postgres")
        sys.exit(1)
    
    if not os.path.exists(excel_file_path):
        logger.error(f"Excel file not found: {excel_file_path}")
        sys.exit(1)
    
    # Step 1: Deploy schema
    if not deploy_schema(connection_string):
        logger.error("Schema deployment failed")
        sys.exit(1)
    
    # Step 2: Update store mappings
    if not update_store_mappings(connection_string):
        logger.error("Store mapping update failed")
        sys.exit(1)
    
    # Step 3: Import data
    logger.info("Starting data import...")
    importer = SalesBudgetImporter(excel_file_path, connection_string)
    if not importer.run_import():
        logger.error("Data import failed")
        sys.exit(1)
    
    # Step 4: Verify setup
    if not verify_setup(connection_string):
        logger.error("Setup verification failed")
        sys.exit(1)
    
    logger.info("="*50)
    logger.info("Sales & Budget Data system setup completed successfully!")
    logger.info("="*50)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Deploy the Supabase function: supabase/functions/sales-budget-data/")
    logger.info("2. Test the dashboard integration")
    logger.info("3. Verify data appears correctly in the UI")
    
    sys.exit(0)

if __name__ == "__main__":
    main()