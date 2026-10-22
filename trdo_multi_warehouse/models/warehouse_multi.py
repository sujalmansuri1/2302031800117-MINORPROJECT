from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        'website_warehouse_rel',
        'website_id',
        'warehouse_id',
        string='Warehouses',
    )

    def _get_product_available_qty(self, product, **kwargs):
        if self.warehouse_ids:
            return sum(
                product.with_context(warehouse_id=wh.id).free_qty
                for wh in self.warehouse_ids
            )
        return super()._get_product_available_qty(product, **kwargs)
