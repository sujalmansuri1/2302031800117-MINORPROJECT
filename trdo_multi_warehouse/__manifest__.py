{
    'name': 'Website Multi Warehouse',
    'version': '18.0.2.0.0',
    'summary': 'Multi-warehouse eCommerce + Warehouse Command Center Dashboard',
    'description': (
        'Assign multiple warehouses to a website and automatically split orders '
        'across warehouses based on stock availability.\n'
        '\n'
        'NEW in v2:\n'
        '  - Estimated delivery date per warehouse shown on the cart page.\n'
        '  - Warehouse Command Center: a premium dark-UI Kanban dashboard in the\n'
        '    Inventory backend with live KPIs, low-stock alerts, top movers and\n'
        '    recent transfers across all configured warehouses.\n'
    ),
    'author': 'TRDO',
    'category': 'Website',
    'depends': ['website_sale', 'website_sale_stock', 'stock', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting.xml',
        'views/dashboard_action.xml',
        'views/cart_delivery_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'trdo_multi_warehouse/static/src/css/warehouse_dashboard.css',
            'trdo_multi_warehouse/static/src/xml/warehouse_dashboard.xml',
            'trdo_multi_warehouse/static/src/js/warehouse_dashboard.js',
        ],
        'web.assets_frontend': [
            'trdo_multi_warehouse/static/src/css/warehouse_dashboard.css',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}