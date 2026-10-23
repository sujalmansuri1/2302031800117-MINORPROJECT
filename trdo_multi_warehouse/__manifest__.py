{
    'name': 'Website Multi Warehouse',
    'version': '18.0.2.0.0',
    'summary': 'Multi-warehouse eCommerce Fulfillment & Stock Availability Validation',
    'description': (
        'Assign multiple warehouses to a website and automatically split orders '
        'across warehouses based on stock availability.\n'
        '\n'
        'Features:\n'
        '  - Stock availability check across all website warehouses on the cart page.\n'
        '  - Alerts and stops checkout/payment if requested quantity is not available.\n'
        '  - Multi-warehouse fulfillment and stock allocation.\n'
    ),
    'author': 'TRDO',
    'category': 'Website',
    'depends': ['website_sale', 'website_sale_stock', 'stock', 'mail'],
    'data': [
        'views/res_config_setting.xml',
        'views/cart_delivery_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'trdo_multi_warehouse/static/src/css/cart_delivery.css',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}