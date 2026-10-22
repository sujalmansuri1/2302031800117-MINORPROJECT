from odoo import models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_cart_and_free_qty(self, product, line=None):
        self.ensure_one()
        if not line and not product:
            return 0, 0
        product = product or line.product_id
        cart_qty = sum(
            self._get_common_product_lines(line, product).mapped('product_uom_qty')
        )
        warehouse_ids = self.website_id.warehouse_ids
        if warehouse_ids:
            free_qty = sum(
                product.with_context(warehouse_id=wh.id).free_qty
                for wh in warehouse_ids
            )
        else:
            free_qty = product.with_context(
                warehouse_id=self.website_id.warehouse_id.id
            ).free_qty
        return cart_qty, free_qty


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        if self._context.get("skip_procurement"):
            return True

        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'
        )
        procurements = []
        handled_lines = self.env['sale.order.line']

        for line in self:
            line = line.with_company(line.company_id)
            if line.state != 'sale' or line.order_id.locked or line.product_id.type != 'consu':
                continue

            website = line.order_id.website_id
            warehouse_ids = website.warehouse_ids if website else False
            if not warehouse_ids or len(warehouse_ids) <= 1:
                continue

            handled_lines |= line

            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(
                    line._prepare_procurement_group_vals()
                )
                line.order_id.procurement_group_id = group_id
            else:
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals['partner_id'] = line.order_id.partner_shipping_id.id
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals['move_type'] = line.order_id.picking_policy
                if updated_vals:
                    group_id.write(updated_vals)

            total_product_qty = line.product_uom_qty - qty
            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            origin = line.order_id.name

            warehouse_stocks = []
            for wh in warehouse_ids:
                available = line.product_id.with_context(warehouse_id=wh.id).free_qty
                if available > 0:
                    warehouse_stocks.append((wh, available))

            warehouse_stocks.sort(key=lambda x: x[1], reverse=True)

            if not warehouse_stocks:
                values = line._prepare_procurement_values(group_id=group_id)
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                    total_product_qty, quant_uom
                )
                procurements += line._create_procurements(
                    product_qty, procurement_uom, origin, values
                )
                continue

            qty_remaining = total_product_qty
            for warehouse, available_qty in warehouse_stocks:
                if qty_remaining <= 0:
                    break

                qty_to_allocate = min(qty_remaining, available_qty)
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                    qty_to_allocate, quant_uom
                )

                values = line._prepare_procurement_values(group_id=group_id)
                values['warehouse_id'] = warehouse

                procurements += line._create_procurements(
                    product_qty, procurement_uom, origin, values
                )
                qty_remaining -= qty_to_allocate

            if qty_remaining > 0:
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                    qty_remaining, quant_uom
                )
                values = line._prepare_procurement_values(group_id=group_id)
                procurements += line._create_procurements(
                    product_qty, procurement_uom, origin, values
                )

        remaining_lines = self - handled_lines
        if remaining_lines:
            super(SaleOrderLine, remaining_lines)._action_launch_stock_rule(
                previous_product_uom_qty=previous_product_uom_qty
            )

        if procurements:
            self.env['procurement.group'].run(procurements)

        orders = handled_lines.mapped('order_id')
        for order in orders:
            pickings_to_confirm = order.picking_ids.filtered(
                lambda p: p.state not in ['cancel', 'done']
            )
            if pickings_to_confirm:
                pickings_to_confirm.action_confirm()

        return True