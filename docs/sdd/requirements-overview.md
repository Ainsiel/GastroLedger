# Requirements Overview

## Vision

Provide a trusted operational ledger for restaurant groups that connects recipes,
lots, purchases, production, sales consumption and physical inventory.

## Actors

| Actor | Primary responsibility |
|---|---|
| Tenant administrator | Company settings, users, roles, branches and warehouses |
| Branch manager | Local approvals, cash review, inventory and performance |
| Chef / production lead | Recipes, yields and production batches |
| Warehouse operator | Receiving, transfers, waste and physical counts |
| Purchasing manager | Suppliers, purchase suggestions and orders |
| Workforce coordinator | Schedules and attendance |
| Franchise controller | Royalty estimates and ordering holds |
| Analyst | Cost variance and menu engineering |
| Background worker | Cost recalculation, alerts, imports and projections |

## In Scope

- multi-tenant company registration and scoped access;
- organization, branches and warehouses;
- units, ingredients, recipes, yields and menu costing;
- suppliers, purchasing, receiving and operational returns;
- lots, movements, production, transfers, waste, expiry and physical counts;
- simulated/CSV sales consumption, cash records and workforce operations;
- non-financial franchise controls and profitability analytics.

## Explicit Exclusions

- real payment, subscription, banking or collection transactions;
- POS, accounting, tax, payroll and formal invoicing;
- external APIs and SaaS providers;
- native mobile apps;
- arbitrary recipe recursion deeper than one sub-recipe level;
- negative stock as normal operation.

## Constraints

- Web frontend: Next.js.
- Backend: FastAPI.
- Database: PostgreSQL.
- First version must remain within 15-30 use cases.
- All tenant-owned data is isolated.
- All inventory changes are traceable.
