#!/usr/bin/env python3
"""
Import Cascadia Daily Sales & Budget Data from Excel file
This script reads the Excel file and imports both historical and forecast data into the database
"""

import pandas as pd
import psycopg2
import os
import sys
from datetime import datetime, date
import json
import logging
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sales_budget_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SalesBudgetImporter:
    def __init__(self, excel_file_path: str, connection_string: str):
        self.excel_file_path = excel_file_path
        self.connection_string = connection_string
        self.conn = None
        
        # Store mapping from Excel headers to standardized names
        self.store_mapping = {
            'Colwood': 'Colwood',
            'Quadra': 'Quadra',
            'Crown': 'Crown',
            'Uptown': 'Uptown',
            'Langford': 'Langford',
            'Eagle Creek': 'Eagle Creek',
            'Nanoose': 'Nanoose',
            'Parksville': 'Parksville',
            'Caddy Bay': 'Caddy Bay',
            'Port A': 'Port A',
            'Royal B': 'Royal B',
            'Allandale': 'Allandale',
            'Bear': 'Bear'
        }
        
        # Day mapping
        self.day_mapping = {
            'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4,
            'Thursday': 5, 'Friday': 6, 'Saturday': 7
        }

    def connect_database(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("Database connection established")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def read_excel_data(self) -> pd.DataFrame:
        """Read and parse the Excel file"""
        try:
            logger.info(f"Reading Excel file: {self.excel_file_path}")
            df = pd.read_excel(self.excel_file_path, sheet_name='FCST FY26', header=None)
            logger.info(f"Excel file loaded with shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            raise

    def parse_excel_structure(self, df: pd.DataFrame) -> Dict:
        """Parse the Excel structure to identify store columns and data layout"""
        structure = {
            'store_columns': {},
            'date_columns': {},
            'data_start_row': 3  # Based on analysis, data starts at row 3 (0-indexed)
        }
        
        # Parse store headers from row 0
        for i, col_value in enumerate(df.iloc[0]):
            if isinstance(col_value, str) and col_value.strip():
                store_name = col_value.strip()
                if store_name in self.store_mapping:
                    structure['store_columns'][i] = self.store_mapping[store_name]
                    logger.info(f"Found store column {i}: {store_name}")
        
        # Parse date/structure information
        structure['date_columns'] = {
            'day_number': 0,
            'day_name': 1,
            'fy25_date': 2,
            'fy26_date': 3,
            'day_number_fy26': 4,
            'day_name_fy26': 5
        }
        
        logger.info(f"Parsed structure: {len(structure['store_columns'])} stores found")
        return structure

    def extract_variance_adjustments(self, df: pd.DataFrame, structure: Dict) -> Dict:
        """Extract variance adjustment factors from row 1"""
        adjustments = {}
        
        for col_idx, store_name in structure['store_columns'].items():
            if col_idx < len(df.columns):
                adjustment_value = df.iloc[1, col_idx]
                if pd.notna(adjustment_value) and isinstance(adjustment_value, (int, float)):
                    adjustments[store_name] = float(adjustment_value)
                    logger.info(f"Variance adjustment for {store_name}: {adjustment_value}")
                else:
                    adjustments[store_name] = 0.0
        
        return adjustments

    def process_data_rows(self, df: pd.DataFrame, structure: Dict, variance_adjustments: Dict) -> Tuple[List, List]:
        """Process each data row and prepare for database insertion"""
        historical_data = []
        forecast_data = []
        
        start_row = structure['data_start_row']
        
        for row_idx in range(start_row, len(df)):
            try:
                # Extract date information
                day_number = df.iloc[row_idx, structure['date_columns']['day_number']]
                day_name = df.iloc[row_idx, structure['date_columns']['day_name']]
                fy25_date = df.iloc[row_idx, structure['date_columns']['fy25_date']]
                fy26_date = df.iloc[row_idx, structure['date_columns']['fy26_date']]
                
                # Skip rows without valid date data
                if pd.isna(day_number) or pd.isna(day_name) or pd.isna(fy25_date) or pd.isna(fy26_date):
                    continue
                
                # Convert to proper types
                day_num = int(day_number) if pd.notna(day_number) else None
                day_name_str = str(day_name).strip() if pd.notna(day_name) else None
                
                # Convert dates
                if isinstance(fy25_date, datetime):
                    fy25_date_obj = fy25_date.date()
                elif isinstance(fy25_date, str):
                    fy25_date_obj = datetime.strptime(fy25_date, '%Y-%m-%d').date()
                else:
                    continue
                    
                if isinstance(fy26_date, datetime):
                    fy26_date_obj = fy26_date.date()
                elif isinstance(fy26_date, str):
                    fy26_date_obj = datetime.strptime(fy26_date, '%Y-%m-%d').date()
                else:
                    continue
                
                # Process each store's data
                for col_idx, store_name in structure['store_columns'].items():
                    if col_idx < len(df.columns):
                        # FY25 actual data (historical)
                        fy25_value = df.iloc[row_idx, col_idx]
                        if pd.notna(fy25_value) and isinstance(fy25_value, (int, float)) and fy25_value > 0:
                            historical_data.append({
                                'store_name': store_name,
                                'sale_date': fy25_date_obj,
                                'day_of_week': day_name_str,
                                'day_number': day_num,
                                'fiscal_year': 2025,
                                'sales_amount': float(fy25_value),
                                'data_type': 'actual'
                            })
                        
                        # FY26 forecast data (if next column exists)
                        if col_idx + 1 < len(df.columns):
                            fy26_value = df.iloc[row_idx, col_idx + 1]
                            if pd.notna(fy26_value) and isinstance(fy26_value, (int, float)) and fy26_value > 0:
                                forecast_data.append({
                                    'store_name': store_name,
                                    'forecast_date': fy26_date_obj,
                                    'day_of_week': day_name_str,
                                    'day_number': day_num,
                                    'fiscal_year': 2026,
                                    'forecast_amount': float(fy26_value),
                                    'variance_adjustment': variance_adjustments.get(store_name, 0.0),
                                    'forecast_type': 'daily'
                                })
                
            except Exception as e:
                logger.warning(f"Error processing row {row_idx}: {e}")
                continue
        
        logger.info(f"Processed {len(historical_data)} historical records and {len(forecast_data)} forecast records")
        return historical_data, forecast_data

    def insert_historical_data(self, historical_data: List[Dict]) -> bool:
        """Insert historical sales data into database"""
        if not historical_data:
            logger.info("No historical data to insert")
            return True
            
        try:
            cursor = self.conn.cursor()
            
            insert_sql = """
                SELECT import_daily_sales_data(
                    %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            success_count = 0
            for record in historical_data:
                try:
                    cursor.execute(insert_sql, (
                        record['store_name'],
                        record['sale_date'],
                        record['day_of_week'],
                        record['day_number'],
                        record['fiscal_year'],
                        record['sales_amount'],
                        record['data_type']
                    ))
                    result = cursor.fetchone()
                    if result and result[0]:
                        success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to insert historical record: {e}")
                    continue
            
            self.conn.commit()
            logger.info(f"Successfully inserted {success_count} historical records")
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert historical data: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def insert_forecast_data(self, forecast_data: List[Dict]) -> bool:
        """Insert forecast/budget data into database"""
        if not forecast_data:
            logger.info("No forecast data to insert")
            return True
            
        try:
            cursor = self.conn.cursor()
            
            insert_sql = """
                SELECT import_budget_forecast_data(
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            success_count = 0
            for record in forecast_data:
                try:
                    cursor.execute(insert_sql, (
                        record['store_name'],
                        record['forecast_date'],
                        record['day_of_week'],
                        record['day_number'],
                        record['fiscal_year'],
                        record['forecast_amount'],
                        record['variance_adjustment'],
                        record['forecast_type']
                    ))
                    result = cursor.fetchone()
                    if result and result[0]:
                        success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to insert forecast record: {e}")
                    continue
            
            self.conn.commit()
            logger.info(f"Successfully inserted {success_count} forecast records")
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert forecast data: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def run_import(self) -> bool:
        """Main import process"""
        try:
            logger.info("Starting sales and budget data import")
            
            # Connect to database
            if not self.connect_database():
                return False
            
            # Read Excel data
            df = self.read_excel_data()
            
            # Parse structure
            structure = self.parse_excel_structure(df)
            
            # Extract variance adjustments
            variance_adjustments = self.extract_variance_adjustments(df, structure)
            
            # Process data rows
            historical_data, forecast_data = self.process_data_rows(df, structure, variance_adjustments)
            
            # Insert data
            historical_success = self.insert_historical_data(historical_data)
            forecast_success = self.insert_forecast_data(forecast_data)
            
            if historical_success and forecast_success:
                logger.info("Import completed successfully")
                return True
            else:
                logger.error("Import completed with errors")
                return False
                
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False
        finally:
            self.close_connection()

def main():
    """Main entry point"""
    # Configuration
    excel_file_path = r"C:\Users\Jay\OneDrive - trufflesgroupttg\Database Design & Planning Documents\Cascadia Daily Sales & Budget Data.xlsx"
    
    # Get database connection string from environment or config
    connection_string = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/database')
    
    if connection_string == 'postgresql://username:password@localhost:5432/database':
        logger.error("Please set DATABASE_URL environment variable with your Supabase connection string")
        sys.exit(1)
    
    # Run import
    importer = SalesBudgetImporter(excel_file_path, connection_string)
    success = importer.run_import()
    
    if success:
        logger.info("Sales and budget data import completed successfully")
        sys.exit(0)
    else:
        logger.error("Sales and budget data import failed")
        sys.exit(1)

if __name__ == "__main__":
    main()