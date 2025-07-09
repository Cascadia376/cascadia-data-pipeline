# Cascadia Data Pipeline - Database Schema Reference

## Overview
This document provides a comprehensive reference for the Cascadia retail data pipeline database schema. The schema is designed to support daily sales reporting, inventory management, automated reordering, and planogram analytics.

## Core Entity Relationships

```
Store (1) ←→ (M) SalesSummary
Store (1) ←→ (M) Inventory  
Store (1) ←→ (M) ProductPlacement
Product (1) ←→ (M) SalesSummary
Product (1) ←→ (M) Inventory
Supplier (1) ←→ (M) Product
```

## Table Definitions

### **Core Business Tables**

#### `store`
**Purpose:** Master table for all retail locations
```sql
store_id (PK)          - Auto-incrementing store identifier
name                   - Store name (UNIQUE)
location               - Physical address/description
timezone               - Store timezone (default: America/Los_Angeles)
status                 - Store status (default: active)
access_code            - Unique access code for store operations
```

#### `product`
**Purpose:** Master product catalog
```sql
sku (PK)               - Stock Keeping Unit identifier
product_name           - Product display name
size                   - Product size/variant
units_per_case         - Units contained in one case
default_supplier_id    - FK to supplier table
is_active              - Product active status (default: true)
last_cost              - Most recent purchase cost
average_cost           - Rolling average cost
```

#### `supplier`
**Purpose:** Vendor/supplier master data
```sql
supplier_id (PK)       - Auto-incrementing supplier identifier
name                   - Supplier company name
contact_info           - Contact details
delivery_terms         - Delivery terms and conditions
```

### **Transactional Data Tables**

#### `salessummary` ⭐ **PRIMARY PIPELINE TABLE**
**Purpose:** Daily aggregated sales data by store/SKU
```sql
store_id (PK)          - FK to store table
sku (PK)               - FK to product table  
date (PK)              - Sales date
units_sold             - Total units sold
total_sales            - Total sales revenue
```
**Composite Primary Key:** `(store_id, sku, date)`
**Pipeline SLA:** Data available by 9 AM daily

#### `inventory` ⭐ **PRIMARY PIPELINE TABLE**
**Purpose:** Current inventory levels by store/SKU
```sql
store_id (PK)          - FK to store table
sku (PK)               - FK to product table
quantity_on_hand_units - Current inventory count
last_counted_at        - Timestamp of last inventory count
```
**Composite Primary Key:** `(store_id, sku)`

### **Pricing & Cost Tables**

#### `retailprice`
**Purpose:** Current and historical retail pricing
```sql
sku (PK)               - FK to product table
store_id (PK)          - FK to store table
price_type (PK)        - Price type (default: 'current')
price                  - Retail price amount
start_date             - Price effective start date
end_date               - Price effective end date
```

#### `retailpricehistory`
**Purpose:** Audit trail for price changes
```sql
sku                    - FK to product table
store_id               - FK to store table
price_type             - Type of price change
old_price              - Previous price
new_price              - New price
change_date            - Date of price change
reason                 - Reason for price change
```

### **Inventory Management Tables**

#### `reorderpolicy`
**Purpose:** Store-specific reordering rules
```sql
store_id (PK)          - FK to store table
sku (PK)               - FK to product table
min_qty                - Minimum quantity threshold
reorder_multiplier     - Multiplier for reorder calculations
assigned_rule_id       - FK to reorderrule table
do_not_reorder         - Flag to prevent automatic reordering
```

#### `reorderrule`
**Purpose:** Master reordering rule definitions
```sql
rule_id (PK)           - Auto-incrementing rule identifier
rule_name              - Rule display name
description            - Rule description
logic_reference        - Reference to business logic implementation
```

#### `purchaseorder`
**Purpose:** Purchase order header information
```sql
purchase_order_id (PK) - Auto-incrementing PO identifier
store_id               - FK to store table
supplier_id            - FK to supplier table
status                 - PO status
created_by             - User who created the PO
expected_delivery_date - Expected delivery date
```

#### `purchaseorderline`
**Purpose:** Individual line items on purchase orders
```sql
purchase_order_id (PK) - FK to purchaseorder table
sku (PK)               - FK to product table
ordered_cases          - Number of cases ordered
case_cost              - Cost per case
received_cases         - Number of cases received
```

### **Customer & Transaction Tables**

#### `guest`
**Purpose:** Customer loyalty and profile data
```sql
guest_id (PK)          - Unique guest identifier
email                  - Customer email
phone                  - Customer phone
loyalty_tier           - Loyalty program tier
created_at             - Account creation timestamp
opted_in               - Marketing opt-in status
last_seen_at           - Last transaction timestamp
total_spend            - Lifetime spend amount
total_visits           - Total visit count
notes                  - Customer notes
```

#### `guesttransaction`
**Purpose:** Individual customer transactions
```sql
transaction_id (PK)    - Auto-incrementing transaction ID
guest_id               - FK to guest table
store_id               - FK to store table
timestamp              - Transaction timestamp
basket_size            - Number of items in basket
total_spend            - Total transaction amount
source                 - Transaction source/channel
registered_staff_id    - Staff member who processed transaction
```

#### `guesttransactionline`
**Purpose:** Individual items within customer transactions
```sql
transaction_id (PK)    - FK to guesttransaction table
sku (PK)               - FK to product table
quantity               - Quantity purchased
unit_price             - Price per unit
final_price            - Final price after discounts
promo_applied          - Promotion applied flag
loyalty_discount       - Loyalty discount applied flag
```

### **Product Management Tables**

#### `productbarcode`
**Purpose:** Barcode mappings for products
```sql
barcode (PK)           - Barcode value
sku                    - FK to product table
barcode_type           - Barcode type (default: 'UPC')
supplier_id            - FK to supplier table
is_active              - Barcode active status
notes                  - Additional notes
```

#### `productdeposit`
**Purpose:** Deposit amounts for returnable products
```sql
sku (PK)               - FK to product table
deposit_per_unit       - Deposit amount per unit
last_updated           - Last update timestamp
```

#### `attributetype`
**Purpose:** Product attribute type definitions
```sql
attribute_type_id (PK) - Auto-incrementing attribute type ID
name                   - Attribute type name
applies_to             - What entity this applies to
description            - Attribute type description
```

#### `attributevalue`
**Purpose:** Specific values for attribute types
```sql
attribute_value_id (PK)- Auto-incrementing attribute value ID
attribute_type_id      - FK to attributetype table
value                  - Attribute value
description            - Value description
active                 - Value active status
```

#### `productattributeassignment`
**Purpose:** Assignment of attributes to products
```sql
sku (PK)               - FK to product table
attribute_value_id (PK)- FK to attributevalue table
priority               - Assignment priority
is_primary             - Primary attribute flag
```

### **Planogram & Location Tables**

#### `storelocation`
**Purpose:** Physical locations within stores
```sql
store_id (PK)          - FK to store table
location_code (PK)     - Location identifier within store
location_type          - Type of location (shelf, endcap, etc.)
planogram_zone         - Planogram zone designation
dimensions             - Physical dimensions
active                 - Location active status
```

#### `productplacement`
**Purpose:** Product placement within store locations
```sql
store_id (PK)          - FK to store table
sku (PK)               - FK to product table
location_code (PK)     - Location within store
location_type          - Type of location
placement_start        - Placement start date
placement_end          - Placement end date
is_primary_location    - Primary location flag
facings                - Number of facings
notes                  - Placement notes
```

### **Operational Tables**

#### `shrinkevent`
**Purpose:** Inventory shrinkage tracking
```sql
shrink_event_id (PK)   - Auto-incrementing shrink event ID
store_id               - FK to store table
sku                    - FK to product table
shrink_date            - Date of shrinkage
quantity_lost_units    - Units lost
reason_code            - Reason for shrinkage
entered_by             - User who entered the record
reference_doc          - Reference document
notes                  - Additional notes
```

#### `invoice`
**Purpose:** Supplier invoice tracking
```sql
invoice_id (PK)        - Auto-incrementing invoice ID
supplier_id            - FK to supplier table
purchase_order_id      - FK to purchaseorder table
invoice_date           - Invoice date
total_invoice_value    - Total invoice amount
status                 - Invoice status
issue_flag             - Issue flag
issue_type             - Type of issue
issue_notes            - Issue notes
```

#### `invoicediscrepancy`
**Purpose:** Invoice discrepancy tracking
```sql
invoice_id (PK)        - FK to invoice table
sku (PK)               - FK to product table
discrepancy_type       - Type of discrepancy
expected_cases         - Expected case count
invoiced_cases         - Invoiced case count
resolved               - Resolution status
resolution_date        - Date resolved
credit_memo_number     - Credit memo reference
```

#### `labelqueue`
**Purpose:** Label printing queue management
```sql
id (PK)                - UUID identifier
store_id               - FK to store table
sku                    - FK to product table
quantity               - Number of labels to print
created_at             - Queue entry timestamp
updated_at             - Last update timestamp
```

## Key Indexes & Performance Considerations

### **Critical Indexes for Pipeline Performance**
```sql
-- Sales summary daily queries
CREATE INDEX idx_salessummary_date ON salessummary(date);
CREATE INDEX idx_salessummary_store_date ON salessummary(store_id, date);

-- Inventory lookups
CREATE INDEX idx_inventory_store ON inventory(store_id);
CREATE INDEX idx_inventory_last_counted ON inventory(last_counted_at);

-- Product lookups
CREATE INDEX idx_product_active ON product(is_active);
CREATE INDEX idx_product_supplier ON product(default_supplier_id);
```

## Data Pipeline Integration Points

### **Daily Ingestion Tables**
1. **`salessummary`** - Primary sales data ingestion target
2. **`inventory`** - Daily inventory snapshot updates
3. **`retailprice`** - Price updates and changes

### **Reordering Pipeline Tables**
1. **`reorderpolicy`** - Store-specific reordering rules
2. **`inventory`** - Current stock levels
3. **`salessummary`** - Sales velocity calculations
4. **`purchaseorder`** - Generated purchase orders

### **Analytics & Reporting Tables**
1. **`productplacement`** - Planogram analytics
2. **`guesttransaction`** - Customer behavior analysis
3. **`shrinkevent`** - Loss prevention reporting

## Schema Maintenance Notes

- **Foreign Key Constraints:** All relationships enforced at database level
- **Data Types:** Numeric fields use `numeric` type for precision
- **Timestamps:** All timestamps are `timestamp without time zone`
- **Defaults:** Sensible defaults provided for operational fields
- **Sequences:** Auto-incrementing IDs use PostgreSQL sequences

This schema supports the full retail operations pipeline from daily sales ingestion through advanced planogram analytics.
```

```markdown:AGENTS.md
# CODEX Agents Guide for Cascadia Data Pipeline

## Overview
This document provides specific prompts and guidance for using CODEX Agents to accelerate development of the Cascadia retail data pipeline. Each agent specialization is designed to handle specific components of the system.

---

## 🗄️ **Database Agent**

### **Agent Specialization:** PostgreSQL/Supabase Schema & Queries

### **Current Status:** ✅ Schema Complete
The database schema is already defined. Use this agent for:

#### **Prompt Templates:**

**For Index Optimization:**
```
"Analyze the Cascadia retail database schema and create optimized indexes for:
1. Daily sales summary queries filtering by date and store_id
2. Inventory lookups by store and SKU
3. Reorder policy queries joining inventory and sales data
4. Product placement analytics queries

Include CREATE INDEX statements and explain the performance impact."
```

**For Sample Data Generation:**
```
"Generate realistic sample data for the Cascadia retail database with:
- 5 stores with different characteristics
- 100 products across various categories
- 30 days of sales data with realistic patterns
- Current inventory levels
- Reorder policies for all store/SKU combinations

Provide INSERT statements that respect all foreign key constraints."
```

**For Query Optimization:**
```
"Create optimized SQL queries for the Cascadia pipeline:
1. Daily sales dashboard aggregations by store and category
2. Inventory reorder recommendations based on sales velocity
3. Out-of-stock alerts with supplier information
4. Top performing products by store with placement data

Include execution plans and performance considerations."
```

---

## 🚀 **FastAPI Backend Agent**

### **Agent Specialization:** Python FastAPI Development

### **Current Status:** 🔲 Not Started

#### **Initial Setup Prompt:**
```
"Create a complete FastAPI project structure for a retail data pipeline with:

PROJECT STRUCTURE:
- /app (main application)
- /app/api/v1 (API routes)
- /app/core (configuration, database)
- /app/models (Pydantic models)
- /app/services (business logic)
- /app/utils (utilities)

REQUIREMENTS:
1. Supabase PostgreSQL connection using asyncpg
2. CSV file upload endpoints for sales and inventory data
3. Pydantic models matching the provided database schema
4. Error handling and logging
5. CORS configuration for Next.js frontend
6. Environment-based configuration
7. Health check endpoints

SPECIFIC ENDPOINTS NEEDED:
- POST /api/v1/ingest/sales (CSV upload)
- POST /api/v1/ingest/inventory (CSV upload)
- GET /api/v1/dashboard/sales-summary
- GET /api/v1/dashboard/inventory-alerts
- GET /api/v1/reorder/recommendations

Include requirements.txt, Dockerfile, and deployment configuration for Vercel."
```

#### **Data Validation Prompt:**
```
"Create comprehensive Pydantic models and validation for the Cascadia retail pipeline:

MODELS NEEDED:
1. SalesSummaryCreate - for CSV ingestion validation
2. InventoryCreate - for inventory snapshot validation
3. ProductResponse - for API responses
4. StoreResponse - for store data
5. ReorderRecommendation - for reorder suggestions

VALIDATION REQUIREMENTS:
- SKU format validation (alphanumeric, length constraints)
- Date validation (not future dates for sales)
- Numeric validation (positive values for quantities/prices)
- Store ID validation against existing stores
- Required field validation with meaningful error messages

Include custom validators and error response schemas."
```

#### **Business Logic Prompt:**