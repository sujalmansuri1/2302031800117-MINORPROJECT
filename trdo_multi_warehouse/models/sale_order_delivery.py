from odoo import models
from datetime import date, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_warehouse_delivery_estimate(self):
        self.ensure_one()
        result = {}
        warehouses = self.website_id.warehouse_ids if self.website_id else self.env['stock.warehouse']
        if not warehouses:
            return result

        order_map = {'available': 0, 'partial': 1, 'unavailable': 2}
        for line in self.order_line.filtered(lambda l: l.product_id and l.product_id.type == 'consu'):
            estimates = []
            for wh in warehouses:
                free_qty = line.product_id.with_context(warehouse_id=wh.id).free_qty
                lead_days = int(wh.company_id.security_lead + (line.product_id.sale_delay or 0)) + 1
                ship_date = date.today() + timedelta(days=lead_days)

                if free_qty >= line.product_uom_qty:
                    status, status_label = 'available', 'In Stock'
                elif free_qty > 0:
                    status, status_label = 'partial', 'Partial Stock'
                else:
                    status, status_label = 'unavailable', 'Out of Stock'
                    ship_date += timedelta(days=5)

                estimates.append({
                    'warehouse_id': wh.id,
                    'warehouse_name': wh.name,
                    'warehouse_code': wh.code,
                    'city': wh.partner_id.city or '',
                    'free_qty': round(free_qty, 2),
                    'status': status,
                    'status_label': status_label,
                    'ship_date': ship_date.strftime('%b %d, %Y'),
                    'lead_days': lead_days,
                })

            estimates.sort(key=lambda x: order_map.get(x['status'], 9))
            result[line.id] = {
                'product_name': line.product_id.display_name,
                'ordered_qty': line.product_uom_qty,
                'uom': line.product_uom.name,
                'estimates': estimates,
            }
        return result
