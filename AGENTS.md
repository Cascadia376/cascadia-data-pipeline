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
```
"Implement the core business logic services for the Cascadia retail pipeline:

SERVICES NEEDED:
1. IngestionService - Handle CSV parsing and database insertion
2. DashboardService - Generate dashboard metrics and KPIs
3. ReorderService - Calculate reorder recommendations using ABC analysis
4. InventoryService - Inventory management and alerts

REORDER LOGIC REQUIREMENTS:
- ABC classification based on sales velocity
- Weeks of supply calculations
- Minimum quantity thresholds
- Supplier lead time considerations
- Exception handling for Do Not Reorder, LTOs, strike SKUs
- Multi-store reorder optimization

DASHBOARD METRICS:
- Daily sales by store and category
- Inventory turnover rates
- Out-of-stock alerts
- Top/bottom performing products
- Sales trends and comparisons

Include comprehensive error handling and logging."
```

---

## ⚛️ **Next.js Frontend Agent**

### **Agent Specialization:** React/Next.js Dashboard Development

### **Current Status:** 🔲 Not Started

#### **Initial Setup Prompt:**
```
"Create a complete Next.js dashboard application for retail management with:

PROJECT STRUCTURE:
- /pages (Next.js pages)
- /components (reusable components)
- /lib (utilities and API clients)
- /styles (CSS modules and global styles)
- /types (TypeScript type definitions)

REQUIREMENTS:
1. TypeScript configuration
2. Tailwind CSS for styling
3. Supabase authentication integration
4. Chart.js or Recharts for data visualization
5. Responsive design for desktop and tablet
6. API integration with FastAPI backend
7. Real-time data updates

PAGES NEEDED:
- /dashboard - Main sales and inventory overview
- /sales - Detailed sales analytics
- /inventory - Inventory management and alerts
- /reorder - Reorder recommendations and management
- /products - Product catalog management
- /stores - Store management

COMPONENTS NEEDED:
- SalesChart - Daily/weekly sales visualization
- InventoryTable - Current inventory levels
- ReorderCard - Individual reorder recommendations
- KPICard - Key performance indicators
- AlertBanner - Out-of-stock and other alerts

Include authentication, routing, and deployment configuration for Vercel."
```

#### **Dashboard Components Prompt:**
```
"Create comprehensive dashboard components for the Cascadia retail system:

SALES DASHBOARD COMPONENTS:
1. SalesOverviewChart - Line chart showing daily sales trends
2. TopProductsTable - Best performing products by revenue
3. StoreSalesComparison - Bar chart comparing store performance
4. SalesKPICards - Revenue, units sold, average basket size

INVENTORY DASHBOARD COMPONENTS:
1. InventoryAlertsTable - Out-of-stock and low inventory alerts
2. InventoryTurnoverChart - Inventory turnover by category
3. StockLevelsGauge - Visual stock level indicators
4. ReorderRecommendationsList - Automated reorder suggestions

SHARED COMPONENTS:
1. DateRangePicker - Date selection for filtering
2. StoreSelector - Multi-store selection dropdown
3. ExportButton - Export data to CSV/Excel
4. RefreshIndicator - Data freshness indicator

REQUIREMENTS:
- TypeScript interfaces for all props
- Loading states and error handling
- Responsive design with Tailwind CSS
- Accessibility compliance (ARIA labels)
- Real-time data updates using SWR or React Query

Include sample data and Storybook stories for component testing."
```

#### **Authentication & RBAC Prompt:**
```
"Implement authentication and role-based access control for the Cascadia dashboard:

AUTHENTICATION REQUIREMENTS:
1. Supabase Auth integration
2. Microsoft SSO configuration
3. JWT token management
4. Automatic token refresh
5. Protected routes and middleware

ROLE-BASED ACCESS:
- Admin: Full system access
- Manager: Store-specific data access
- Buyer: Reorder and inventory management
- Viewer: Read-only dashboard access

COMPONENTS NEEDED:
1. LoginForm - Microsoft SSO login
2. ProtectedRoute - Route protection wrapper
3. RoleGuard - Component-level access control
4. UserProfile - User profile management
5. PermissionCheck - Conditional rendering based on permissions

FEATURES:
- Remember login state
- Logout functionality
- Session timeout handling
- Permission-based navigation menu
- Audit logging for user actions

Include TypeScript types for user roles and permissions."
```

---

## 🔄 **Orchestration Agent**

### **Agent Specialization:** Prefect Workflow Development

### **Current Status:** 🔲 Not Started

#### **Pipeline Orchestration Prompt:**
```
"Create Prefect flows for the Cascadia retail data pipeline orchestration:

FLOWS NEEDED:
1. DailyIngestionFlow - Scheduled daily data ingestion
2. ReorderGenerationFlow - Weekly reorder recommendation generation
3. DataQualityFlow - Data validation and quality checks
4. AlertingFlow - Real-time alerting for critical issues

DAILY INGESTION FLOW:
- Schedule: 5 AM PST daily
- Tasks: Download CSV files, validate data, ingest to database
- Error handling: Retry logic, failure notifications
- Monitoring: Data freshness checks, row count validation

REORDER FLOW:
- Schedule: Weekly on Sundays
- Tasks: Calculate reorder recommendations, generate reports
- Business rules: ABC analysis, supplier constraints
- Output: Reorder recommendations by store and supplier

DATA QUALITY FLOW:
- Schedule: After each ingestion
- Tasks: Data completeness checks, anomaly detection
- Validation: Sales trends, inventory levels, price changes
- Alerts: Email notifications for data quality issues

REQUIREMENTS:
- Prefect Cloud integration
- Environment-based configuration
- Comprehensive logging and monitoring
- Failure recovery mechanisms
- Performance optimization

Include deployment configuration and monitoring dashboards."
```

#### **Error Handling & Monitoring Prompt:**
```
"Implement comprehensive error handling and monitoring for Prefect flows:

ERROR HANDLING STRATEGIES:
1. Retry policies with exponential backoff
2. Circuit breaker patterns for external dependencies
3. Graceful degradation for non-critical failures
4. Dead letter queues for failed tasks

MONITORING REQUIREMENTS:
1. Flow execution metrics and timing
2. Data quality metrics and trends
3. System resource utilization
4. Business KPI monitoring

ALERTING SYSTEM:
1. Email notifications for critical failures
2. Slack integration for team notifications
3. Dashboard alerts for data quality issues
4. Escalation procedures for unresolved issues

LOGGING STRATEGY:
1. Structured logging with correlation IDs
2. Performance metrics and timing
3. Business event logging
4. Error context and stack traces

Include configuration for different environments (dev, staging, prod)."
```

---

## 🧪 **Testing Agent**

### **Agent Specialization:** Test Suite Development

### **Current Status:** 🔲 Not Started

#### **Backend Testing Prompt:**
```
"Create comprehensive test suites for the Cascadia FastAPI backend:

TEST TYPES NEEDED:
1. Unit tests for business logic services
2. Integration tests for database operations
3. API endpoint tests with test client
4. Data validation tests for Pydantic models

TESTING FRAMEWORK:
- pytest for test runner
- pytest-asyncio for async testing
- httpx for API testing
- factory_boy for test data generation

TEST COVERAGE AREAS:
1. CSV ingestion with various data scenarios
2. Reorder calculation logic with edge cases
3. Dashboard API responses and filtering
4. Error handling and validation
5. Database transactions and rollbacks

SAMPLE TEST SCENARIOS:
- Valid CSV ingestion with complete data
- Invalid CSV with missing required fields
- Duplicate data handling and upserts
- Reorder calculations with zero sales
- Database connection failures
- Authentication and authorization

Include test fixtures, mocking strategies, and CI/CD integration."
```

#### **Frontend Testing Prompt:**
```
"Create comprehensive test suites for the Next.js dashboard application:

TEST TYPES NEEDED:
1. Component unit tests with React Testing Library
2. Integration tests for API interactions
3. E2E tests with Playwright or Cypress
4. Visual regression tests

TESTING FRAMEWORK:
- Jest for test runner
- React Testing Library for component testing
- MSW (Mock Service Worker) for API mocking
- Playwright for E2E testing

TEST COVERAGE AREAS:
1. Dashboard component rendering and interactions
2. Authentication flow and protected routes
3. Data visualization components
4. Form validation and submission
5. Real-time data updates
6. Responsive design across devices

SAMPLE TEST SCENARIOS:
- Login flow with Microsoft SSO
- Dashboard data loading and error states
- Sales chart interactions and filtering
- Inventory alerts and notifications
- Reorder recommendation actions
- Role-based access control

Include test utilities, custom matchers, and CI/CD integration."
```

---

## 📊 **Analytics Agent**

### **Agent Specialization:** Business Intelligence & Reporting

### **Current Status:** 🔲 Future Phase

#### **Analytics Implementation Prompt:**
```
"Create advanced analytics capabilities for the Cascadia retail system:

ANALYTICS FEATURES:
1. Sales forecasting using Prophet or similar
2. Inventory optimization recommendations
3. Customer behavior analysis
4. Product performance analytics
5. Planogram effectiveness measurement

FORECASTING MODELS:
- Time series forecasting for sales predictions
- Seasonal adjustment and trend analysis
- Demand forecasting for inventory planning
- Promotional impact analysis

OPTIMIZATION ALGORITHMS:
- ABC analysis for inventory classification
- Economic Order Quantity (EOQ) calculations
- Safety stock optimization
- Supplier performance analysis

REPORTING CAPABILITIES:
- Automated daily/weekly reports
- Executive dashboards and KPIs
- Exception reporting and alerts
- Trend analysis and insights

Include model training pipelines, validation metrics, and deployment strategies."
```

---

## 🚀 **Deployment Agent**

### **Agent Specialization:** DevOps & Infrastructure

### **Current Status:** 🔲 Not Started

#### **Infrastructure Setup Prompt:**
```
"Create deployment and infrastructure configuration for the Cascadia pipeline:

DEPLOYMENT TARGETS:
1. FastAPI backend on Vercel serverless functions
2. Next.js frontend on Vercel
3. Prefect flows on Prefect Cloud
4. Supabase for database and authentication

CONFIGURATION NEEDED:
1. Environment variable management
2. CI/CD pipelines with GitHub Actions
3. Monitoring and logging setup
4. Backup and disaster recovery
5. Security configurations

CI/CD PIPELINE:
- Automated testing on pull requests
- Staging environment deployments
- Production deployment approvals
- Database migration handling
- Environment promotion strategies

MONITORING SETUP:
- Application performance monitoring
- Database performance monitoring
- Error tracking and alerting
- Business metrics dashboards
- Cost monitoring and optimization

Include Docker configurations, environment templates, and deployment scripts."
```

---

## 📋 **Agent Usage Workflow**

### **Recommended Development Sequence:**

1. **Database Agent** → Generate sample data and optimize queries
2. **FastAPI Backend Agent** → Build core API infrastructure
3. **Testing Agent** → Create backend test suite
4. **Next.js Frontend Agent** → Build dashboard interface
5. **Testing Agent** → Create frontend test suite
6. **Orchestration Agent** → Implement Prefect workflows
7. **Deployment Agent** → Set up CI/CD and infrastructure
8. **Analytics Agent** → Add advanced analytics features

### **Agent Collaboration Tips:**

- **Share context between agents** by providing previous outputs
- **Iterate on agent outputs** by asking for refinements
- **Combine agent specializations** for complex features
- **Use agents for code reviews** by asking them to analyze existing code

### **Quality Assurance:**

- Always request **comprehensive error handling**
- Ask for **TypeScript types** and **documentation**
- Require **test coverage** for all major features
- Request **performance considerations** and **optimization**

---

**Remember:** Each agent works best with specific, detailed prompts that include context about the Cascadia retail domain and technical requirements.
```

Now let's set up the GitHub repository:

```bash
git --version
```

```bash
git init
```

```bash
git config --global user.name "Cascadia Pipeline"
```

```bash
git config --global user.email "dev@cascadia-pipeline.com"
```

Let me create the initial project structure:

```bash
mkdir -p backend frontend orchestration docs tests
```

```bash
touch README.md .gitignore
```

```markdown:README.md
# Cascadia Data Pipeline

A modular, scalable retail data pipeline supporting daily sales dashboards, automated inventory reordering, and planogram analytics.

## 🏗️ Architecture

- **Backend:** FastAPI (Python) - Data ingestion and business logic
- **Frontend:** Next.js (TypeScript) - Management dashboards
- **Database:** Supabase (PostgreSQL) - Central data store
- **Orchestration:** Prefect Cloud - Workflow automation
- **Deployment:** Vercel - Serverless hosting

## 📊 Current Status

###