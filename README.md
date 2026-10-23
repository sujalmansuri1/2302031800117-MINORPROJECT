# 🏢 Odoo 18 Multi-Warehouse Fulfillment

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-714B67.svg?style=flat-square&logo=odoo&logoColor=white)](https://www.odoo.com)
[![Python Version](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/lgpl-3.0)

A comprehensive enterprise-grade Odoo 18 module that unifies **Multi-Warehouse eCommerce fulfillment**, **intelligent order splitting**, and **real-time cart shipping estimates**.

---

## 🌟 Key Features

### 1. 🌐 Multi-Warehouse eCommerce Stock & Fulfillment
- **Multi-Facility Website Mapping:** Link multiple warehouses to any eCommerce website under *Website Settings*.
- **Aggregated Stock Visibility:** Calculates real-time total available free stock across all designated warehouses rather than relying on a single default location.
- **Automated Order Splitting:** When an order contains items distributed across different warehouses, the system intelligently splits procurements based on on-hand stock and generates separate delivery orders (`stock.picking`) per fulfillment center.

### 2. 🚚 Real-Time Cart Delivery Estimates
- **Dynamic Delivery Date Calculation:** Automatically calculates the expected ship date for every cart line using:
  $$\text{Ship Date} = \text{Today} + \text{Warehouse Security Lead Time} + \text{Product Sales Delay} + 1$$
- **Real-Time Stock Status Badges:**
  - 🟢 **In Stock:** Full inventory available in the warehouse.
  - 🟡 **Partial Stock:** Partially available, split delivery recommended.
  - 🔴 **Out of Stock:** Automatically applies backorder lead buffer (+5 days).
- **Location Awareness:** Displays the warehouse name and city directly inside the customer's cart.

---

## 📐 Architecture & Workflow

```mermaid
graph TD
    A[Customer Adds Product to Cart] --> B[Aggregate Free Stock Across Website Warehouses]
    B --> C[Cart Delivery Estimate Widget Displays Ship Dates & Stock Badges]
    C --> D[Customer Confirms Checkout / Sale Order]
    D --> E{Stock Available in Single Warehouse?}
    E -- Yes --> F[Generate Single Delivery Order]
    E -- No --> G[Smart Allocation: Split Procurements by Available Qty]
    G --> H[Create Warehouse A Picking]
    G --> I[Create Warehouse B Picking]
```

---
