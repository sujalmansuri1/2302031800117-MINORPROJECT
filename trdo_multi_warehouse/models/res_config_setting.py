from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        related='website_id.warehouse_ids',
        readonly=False,
        string='eCommerce Warehouses',
    )