# Database Maintenance Guide

This document outlines recommended indexes, data quality validation queries, performance monitoring queries, and backup procedures for the Cascadia retail production database.

## 1. Optimized Indexes for Daily Pipeline Queries

```sql
-- Sales summary queries filtering by date and store_id
CREATE INDEX IF NOT EXISTS idx_salessummary_store_date_sku
    ON salessummary(store_id, date, sku);

-- Inventory lookups by store and SKU (covers primary key, included for clarity)
CREATE INDEX IF NOT EXISTS idx_inventory_store_sku
    ON inventory(store_id, sku);

-- Reorder policy joins with inventory and sales data
CREATE INDEX IF NOT EXISTS idx_reorderpolicy_store_sku
    ON reorderpolicy(store_id, sku);

-- Product placement analytics queries by store and SKU
CREATE INDEX IF NOT EXISTS idx_productplacement_store_sku
    ON productplacement(store_id, sku);
```

These indexes align with common query patterns in the daily pipeline and reduce sequential scans during joins.

## 2. Data Quality Validation Queries

```sql
-- Ensure no negative quantities in inventory
SELECT store_id, sku, quantity_on_hand_units
FROM inventory
WHERE quantity_on_hand_units < 0;

-- Detect duplicate sales summary records
SELECT store_id, sku, date, COUNT(*)
FROM salessummary
GROUP BY store_id, sku, date
HAVING COUNT(*) > 1;

-- Verify foreign key integrity between inventory and product
SELECT inv.store_id, inv.sku
FROM inventory AS inv
LEFT JOIN product AS p ON p.sku = inv.sku
WHERE p.sku IS NULL;
```

Use these checks after each ingestion run to ensure data integrity.

## 3. Performance Monitoring Queries

```sql
-- Recent ingestion runs and durations
SELECT ingestion_date, record_count, EXTRACT(EPOCH FROM (completed_at - started_at)) AS seconds
FROM audit_log
ORDER BY ingestion_date DESC
LIMIT 10;

-- Row counts for today's data
SELECT 'salessummary' AS table, COUNT(*)
FROM salessummary
WHERE date = CURRENT_DATE
UNION ALL
SELECT 'inventory' AS table, COUNT(*)
FROM inventory
WHERE last_counted_at::date = CURRENT_DATE;
```

These queries provide visibility into ingestion performance and row counts.

## 4. Backup and Safety Procedures

1. **Daily Backups**
   - Schedule a nightly `pg_dump` of the production database to secure storage (e.g., S3).
   - Use the `--format=custom` option for efficient compressed backups.

2. **Point-in-Time Recovery**
   - Enable continuous WAL archiving to allow restoration to any point in time.
   - Test recovery procedures regularly in a staging environment.

3. **Access Controls**
   - Restrict backup and restore permissions to database administrators only.
   - Store credentials in a secrets manager (e.g., Supabase environment variables).

4. **Verification**
   - After each backup, run `pg_restore --list` to verify the archive contents.
   - Maintain logs of backup success or failure for auditing.

Adhering to these steps helps safeguard production data and ensures pipeline reliability.
