# Phase 2: Quick Deployment Guide

## 🚀 **5-Minute Setup to Get Real Budget Data**

### **What This Does**
Replaces mock budget data (110% calculations) with real budget forecasts from your Excel file.

### **Step 1: Database Setup**
**Open**: https://supabase.com/dashboard/project/wobndqnfqtumbyxxtojl/editor

**Run these 3 scripts in order:**

1. **`deploy_to_supabase_manual.sql`** - Creates tables and views
2. **`insert_sample_data.sql`** - Adds sample data 
3. **`test_integration.sql`** - Verifies everything works

### **Step 2: Deploy Function**
**Go to**: Edge Functions → Create new function

**Name**: `sales-budget-data`

**Copy code from**: `supabase/functions/sales-budget-data/index.ts`

### **Step 3: Test Dashboard**
**Refresh your dashboard** - you should see:
- ✅ Budget values different from 110% of sales
- ✅ Real variance percentages like -5%, +1.5%, +3%
- ✅ Store-specific budget performance

## 📊 **Expected Sample Data**
- **Quadra**: $16,424 actual vs $15,603 budget (-5% variance)
- **Crown**: $33,045 actual vs $33,541 budget (+1.5% variance)  
- **Uptown**: $12,047 actual vs $12,408 budget (+3% variance)

## 🔄 **For Full Excel Import**
Once testing works, run:
```bash
# With your database password configured
python setup_sales_budget_system.py
```

This imports your complete Excel dataset instead of sample data.

## 🆘 **Troubleshooting**
- **No changes?** → Check Supabase function is deployed
- **Still 110%?** → Verify test queries return data
- **Errors?** → Check browser console for API errors

---
**Files on GitHub**: https://github.com/Cascadia376/cascadia-data-pipeline