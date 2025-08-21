# Cascadia Data Pipeline – PRD, Roadmap, and User Stories

---

# 📝 **Product Requirements Document (PRD)**

## **Overview**

Build a **modular, scalable data pipeline** to support:

- Daily sales, labour, and inventory dashboards
- Automated inventory reordering recommendations
- Planogram and display analytics (Phase 2)

---

## **Goals & Success Metrics**

| **Outcome**              | **Metrics**                                                                                                                                                                      |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Daily Dashboards**     | Available by 9 AM daily<1% data freshness discrepanciesManager adoption ≥80%User satisfaction ≥4/5                                                                               |
| **Inventory Reordering** | Recommendations avoid OOS/overstock ≥90%Time saved for buyers (baseline TBD post-launch)Report generation time <15 min100% correct handling of Do Not Reorder, LTOs, strike SKUs |
| **Planogram Analytics**  | 100% store placement data input by AugustData completeness for display zone, shelf, facingsPipeline readiness for sales uplift analysis                                          |

---

## **Stakeholders**

- **Product Owner:** You
- **Users:** GMs, Area Managers, Senior Ops Manager, Head Buyer, Merchandiser
- **Executive:** President, CEO

---

## **Scope**

### **Phase 1 (Immediate)**

- Ingest POS sales and inventory data daily
- Process into **Supabase database** by 9 AM
- Build **Next.js + FastAPI dashboard app** deployed on Vercel

### **Phase 2 (Next 1–2 weeks)**

- Automate reordering logic (port Python script to FastAPI)
- Generate per-store reorder recommendations with:
  - ABC rules
  - Weeks of supply multipliers
  - Exceptions (Do Not Reorder, LTOs, strike SKUs)

### **Phase 3 (August)**

- Develop planogram tracking schema and data ingestion forms
- Enable display zone, shelf, facing, section-level analytics

### **Future**

- Forecasting models (Prophet/blended) for predictive replenishment

---

## **Technical Architecture**

| **Component**      | **Technology**                                  | **Notes**                                            |
| ------------------ | ----------------------------------------------- | ---------------------------------------------------- |
| **Ingestion**      | FastAPI scheduled tasks (or Supabase Functions) | Serverless cron for daily ingestion                  |
| **Transformation** | Pandas in FastAPI backend                       | Modular reordering & dashboard metrics logic         |
| **Database**       | Supabase (Postgres)                             | Central data store                                   |
| **Frontend**       | Next.js (Vercel)                                | Manager & buyer dashboards                           |
| **Auth**           | Supabase Auth + Microsoft SSO                   | RBAC enforced                                        |
| **Orchestration**  | Prefect Cloud Free Tier                         | Easy setup, scalable, event-driven                   |
| **Audit Logging**  | Supabase tables                                 | Log reorder runs, dashboard views, placement changes |

---

## **Constraints**

- Single data engineer (you)
- Serverless preferred for cost efficiency
- Daily ingestion SLA of **9 AM**
- Future API integrations when POS supports direct pulls

---

# 🚀 **Technical Roadmap**

| **Week**      | **Deliverables**                                                                                                |
| ------------- | --------------------------------------------------------------------------------------------------------------- |
| **Week 1**    | Finalize PRDConfirm data sources & sample filesDeploy Supabase schema                                           |
| **Week 2**    | Build ingestion pipeline MVPLoad daily sales & inventory dataScaffold dashboard frontend                        |
| **Week 3**    | Complete dashboard core metrics & deploy to VercelPort reorder logic to FastAPIGenerate reorder recommendations |
| **Week 4**    | Implement RBAC with Microsoft SSOLaunch reordering automation                                                   |
| **Weeks 5–6** | Design planogram schema & data input toolIntegrate placement data capture                                       |
| **August**    | Roll out planogram analytics MVPBegin baseline vs display lift analysis                                         |

---

# ✅ **Sprint 1 – User Stories & Acceptance Criteria**

## **Epic:** Daily Ingestion MVP

### **Story 1.1 – Set Up Supabase Schema**

🔲 As a **developer**, I want to deploy the Supabase schema so that the database structure supports ingestion.

**Acceptance Criteria**

- Supabase tables for SalesSummary, Inventory, and supporting entities exist.
- Schema matches current uploaded context.
- Tables tested with sample inserts.

---

### **Story 1.2 – Develop FastAPI Ingestion Endpoint**

🔲 As a **developer**, I want an endpoint to ingest daily sales CSV files so that data is available by 9 AM.

**Acceptance Criteria**

- POST /ingest/sales endpoint accepts CSV upload.
- Uses Pandas to parse file.
- Validates required columns: store_id, sku, date, units_sold, total_sales.
- Inserts new data or upserts existing rows based on composite key (store_id, sku, date).
- Returns success/failure status.

---

### **Story 1.3 – Develop FastAPI Inventory Ingestion Endpoint**

🔲 As a **developer**, I want an endpoint to ingest daily inventory snapshot CSV files.

**Acceptance Criteria**

- POST /ingest/inventory endpoint accepts CSV upload.
- Uses Pandas for parsing and validation.
- Inserts new snapshot data into Inventory table.
- Supports either upsert or replace strategy (to be confirmed operationally).

---

### **Story 1.4 – Implement Prefect Flow**

🔲 As a **developer**, I want a scheduled Prefect flow that triggers daily ingestion automatically.

**Acceptance Criteria**

- Flow scheduled for **5 AM PST daily**.
- Downloads CSV file from test location or S3.
- Calls the ingestion endpoints.
- Updates audit_log table with ingestion results (file name, date, row count, success/failure).

---

### **Story 1.5 – Audit Logging Table**

🔲 As a **developer**, I want an audit log table in Supabase to track ingestion runs.

**Acceptance Criteria**

- Table fields: id (UUID), file_name, ingestion_date, record_count, status, error_log.
- Inserts a log row each time ingestion runs.
- Available for monitoring pipeline health.

---

**End of Document. Ready for implementation.**
```

---

## **As Your Senior Data Engineer - Implementation Plan**

Now that we've clarified this is a greenfield project, let's build this systematically. I'll guide you through using CODEX Agents to accelerate development.

### **Immediate Next Steps:**

**1. First, let's check your current environment and set up the foundation:**

```bash
pwd
```

```bash
ls -la
```

**2. Use CODEX Agent for Database Schema Design:**

I need you to **invoke a CODEX Agent specialized in database design** to:
- Create the complete Supabase schema SQL
- Include all tables: SalesSummary, Inventory, Stores, Products, AuditLog
- Add proper indexes, constraints, and relationships
- Generate sample data for testing

**Prompt for CODEX Database Agent:**
```
"Create a complete PostgreSQL schema for a retail data pipeline with tables for sales summary, inventory snapshots, stores, products, and audit logging. Include proper indexes, foreign keys, and sample INSERT statements for testing."
