# Odoo eCommerce Multi-Warehouse Selector

A custom Odoo module that enables **warehouse-aware product availability and order fulfillment** in eCommerce.  
This module helps customers and operations teams work with multiple warehouses instead of a single default stock source.

## ✨ Key Features

- Multi-warehouse support for Odoo eCommerce flows
- Warehouse-specific stock visibility during online shopping
- Warehouse selection logic for cart/checkout flows
- Better fulfillment routing for sales orders created from website purchases

## ✅ Business Benefits

- Improves customer trust with more accurate stock display
- Reduces failed/partial deliveries caused by wrong stock source selection
- Helps scale eCommerce operations across multiple locations

## 📦 Module Scope

This module is designed for Odoo environments where:

- Products are stocked in more than one warehouse
- Website orders need stock checks based on selected/eligible warehouse
- Sales and inventory teams require clearer warehouse-level fulfillment behavior

## 🧩 Compatibility

- Odoo custom deployment
- eCommerce (`website_sale`) + Inventory/Stock workflows

> If you are using additional custom modules (delivery rules, custom checkout, marketplace connectors), validate integration behavior in a staging environment before production rollout.

## 🚀 Installation

1. Copy the module into your Odoo addons path.
2. Update app/module list from Odoo Apps menu (developer mode).
3. Search and install the module from Apps.
4. Restart Odoo service if needed.

## ⚙️ Configuration (Typical)

1. Configure all warehouses and stock locations in **Inventory**.
2. Ensure products are stocked and available in intended warehouses.
3. Configure website/shop behavior as required by your custom logic:
   - warehouse selection strategy
   - fallback warehouse rules
   - stock visibility rules
4. Test with multiple products and warehouses in a staging environment.

## 🧪 Functional Test Checklist

Use this quick checklist after installation:

- [ ] Product with stock only in Warehouse A
- [ ] Product with stock only in Warehouse B
- [ ] Product with stock in multiple warehouses
- [ ] Checkout flow with warehouse selection/fallback
- [ ] Sales order warehouse assignment from website order
- [ ] Out-of-stock behavior when selected warehouse has zero quantity

## 🛠 Troubleshooting

- **Products appear unavailable online**
  - Verify on-hand/forecast quantity in the target warehouse.
  - Check product publish status on website.
  - Confirm warehouse routing/configuration is correct.

- **Unexpected warehouse on confirmed order**
  - Review fallback logic and warehouse assignment rules.
  - Check custom rules from other installed modules.

- **Checkout inconsistencies**
  - Re-test with a clean browser session.
  - Check custom JavaScript or checkout overrides.

## 📄 License

This module is intended for educational/custom project use.  
Add your preferred license terms here if you plan to distribute it.