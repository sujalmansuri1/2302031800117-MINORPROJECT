# 🏢 Odoo 18 Multi-Warehouse Fulfillment & Cart Stock Validation

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-714B67.svg?style=flat-square&logo=odoo&logoColor=white)](https://www.odoo.com)
[![Python Version](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/lgpl-3.0)

A comprehensive Odoo 18 module that unifies **Multi-Warehouse eCommerce fulfillment**, **intelligent order splitting**, and **real-time cart stock availability validation & payment blocking**.

---

## 🌟 Key Features

### 1. 🌐 Multi-Warehouse eCommerce Stock & Fulfillment
- **Multi-Facility Website Mapping:** Link multiple warehouses to any eCommerce website under *Website Settings*.
- **Aggregated Stock Visibility:** Calculates real-time total available free stock across all designated warehouses rather than relying on a single default location.
- **Automated Order Splitting:** When an order contains items distributed across different warehouses, the system intelligently splits procurements based on on-hand stock and generates separate delivery orders (`stock.picking`) per fulfillment center.

### 2. 🛒 Cart Stock Availability & Payment Protection
- **Simple Customer Stock Status:** Displays clear stock indicators (🟢 *In Stock* vs 🔴 *Out of Stock*) without exposing internal warehouse names or facility details to customers.
- **Over-Quantity Prevention:** If a customer adds more items than the total free stock available across all mapped warehouses:
  - An alert banner is displayed warning them that the requested quantity exceeds available stock.
  - The cart line indicates the available vs requested quantity.
  - The **Proceed to Checkout** button is automatically disabled.
  - Access to payment (`/shop/checkout`, `/shop/payment`) is completely blocked, redirecting them back to `/shop/cart` until quantities are adjusted.

---

## 📐 Architecture & Workflow

```mermaid
graph TD
    A[Customer Adds Product to Cart] --> B[Aggregate Free Stock Across Website Warehouses]
    B --> C{Cart Quantity <= Total Stock Across Warehouses?}
    C -- No --> D[Show Stock Alert & Block Proceed to Payment]
    C -- Yes --> E[Allow Checkout & Proceed to Payment]
    E --> F[Customer Confirms Checkout / Sale Order]
    F --> G{Stock Available in Single Warehouse?}
    G -- Yes --> H[Generate Single Delivery Order]
    G -- No --> I[Smart Allocation: Split Procurements by Available Qty]
    I --> J[Create Warehouse A Picking]
    I --> K[Create Warehouse B Picking]
```

---
