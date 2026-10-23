from odoo import models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


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
        warehouse_ids = (
            self.website_id.warehouse_ids
            if self.website_id and self.website_id.warehouse_ids
            else self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)])
        )
        if warehouse_ids:
            free_qty = sum(
                product.with_context(warehouse_id=wh.id).free_qty
                for wh in warehouse_ids
            )
        else:
            default_wh = self.website_id.warehouse_id if self.website_id else self.warehouse_id
            free_qty = product.with_context(
                warehouse_id=default_wh.id if default_wh else False
            ).free_qty
        return cart_qty, free_qty

    def _get_warehouse_delivery_estimate(self):
        """ Backward-compatibility method in case old QWeb template is cached in DB """
        return {}

    def _get_insufficient_stock_lines(self):
        self.ensure_one()
        insufficient = self.env['sale.order.line']
        for line in self.order_line:
            if not line.product_id or line.product_id.type != 'consu':
                continue
            cart_qty, free_qty = self._get_cart_and_free_qty(line.product_id, line=line)
            if line.product_uom_qty > free_qty or cart_qty > free_qty:
                insufficient |= line
        return insufficient

    def _is_cart_ready(self):
        if self._get_insufficient_stock_lines():
            return False
        return super()._is_cart_ready()

    def _check_cart_is_ready_to_be_paid(self):
        insufficient = self._get_insufficient_stock_lines()
        if insufficient:
            raise ValidationError(
                _("Some products in your cart exceed total available stock across our warehouses. "
                  "Please adjust the quantities before proceeding to checkout.")
            )
        return super()._check_cart_is_ready_to_be_paid()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_multi_warehouse_availability(self):
        self.ensure_one()
        if not self.product_id or self.product_id.type != 'consu':
            return {'available': True, 'free_qty': 0, 'is_blocked': False, 'label': ''}

        cart_qty, free_qty = self.order_id._get_cart_and_free_qty(self.product_id, line=self)
        available_qty = max(free_qty, 0.0)
        formatted_free = int(available_qty) if available_qty.is_integer() else available_qty
        formatted_requested = int(self.product_uom_qty) if self.product_uom_qty.is_integer() else self.product_uom_qty

        if self.product_uom_qty > free_qty or cart_qty > free_qty:
            if available_qty <= 0:
                label = _("Out of Stock")
            else:
                label = _(
                    "Only %(available)s available in stock (Requested: %(requested)s)",
                    available=formatted_free,
                    requested=formatted_requested,
                )
            return {
                'available': False,
                'free_qty': available_qty,
                'is_blocked': True,
                'label': label,
            }

        return {
            'available': True,
            'free_qty': available_qty,
            'is_blocked': False,
            'label': _("In Stock"),
        }

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
            if website and website.warehouse_ids:
                warehouse_ids = website.warehouse_ids
            else:
                warehouse_ids = self.env['stock.warehouse'].search([
                    ('company_id', '=', line.company_id.id)
                ])

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

            # Prioritize warehouse with the largest on-hand free quantity
            warehouse_stocks.sort(key=lambda x: x[1], reverse=True)

            if not warehouse_stocks:
                values = line._prepare_procurement_values(group_id=group_id)
                fallback_wh = line.order_id.warehouse_id or warehouse_ids[0]
                values['warehouse_id'] = fallback_wh
                if fallback_wh.delivery_route_id:
                    values['route_ids'] = fallback_wh.delivery_route_id
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
                if warehouse.delivery_route_id:
                    values['route_ids'] = warehouse.delivery_route_id

                procurements += line._create_procurements(
                    product_qty, procurement_uom, origin, values
                )
                qty_remaining -= qty_to_allocate

            if qty_remaining > 0:
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                    qty_remaining, quant_uom
                )
                values = line._prepare_procurement_values(group_id=group_id)
                fallback_wh = line.order_id.warehouse_id or warehouse_ids[0]
                values['warehouse_id'] = fallback_wh
                if fallback_wh.delivery_route_id:
                    values['route_ids'] = fallback_wh.delivery_route_id
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