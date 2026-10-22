from odoo import models, fields, api
from datetime import date, timedelta


class WarehouseDashboard(models.Model):
    _name = 'trdo.warehouse.dashboard'
    _description = 'Multi-Warehouse Dashboard'

    @api.model
    def get_dashboard_data(self):
        warehouses = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)])
        return {
            'warehouses': [self._build_warehouse_card(wh) for wh in warehouses],
            'summary': self._build_summary(warehouses),
            'top_movers': self._get_top_movers(warehouses),
            'low_stock': self._get_low_stock_products(warehouses),
            'recent_transfers': self._get_recent_transfers(warehouses),
        }

    def _build_warehouse_card(self, wh):
        Picking = self.env['stock.picking']
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        now = fields.Datetime.now()

        pending = Picking.search_count([
            ('picking_type_id.warehouse_id', '=', wh.id),
            ('state', 'in', ('assigned', 'waiting', 'confirmed')),
        ])
        done_today = Picking.search_count([
            ('picking_type_id.warehouse_id', '=', wh.id),
            ('state', '=', 'done'),
            ('date_done', '>=', fields.Datetime.to_string(today_start)),
        ])
        overdue = Picking.search_count([
            ('picking_type_id.warehouse_id', '=', wh.id),
            ('state', 'not in', ('done', 'cancel')),
            ('scheduled_date', '<', now),
        ])
        quants = self.env['stock.quant'].search([
            ('location_id', 'child_of', wh.lot_stock_id.id),
            ('quantity', '>', 0),
        ])
        orderpoints = self.env['stock.warehouse.orderpoint'].search([('warehouse_id', '=', wh.id)])
        low_stock_count = sum(1 for op in orderpoints if op.qty_on_hand <= op.product_min_qty)
        max_qty = sum(op.product_max_qty for op in orderpoints) or 1
        on_hand = sum(op.qty_on_hand for op in orderpoints)
        utilization = min(round((on_hand / max_qty) * 100, 1), 100) if orderpoints else 0

        return {
            'id': wh.id,
            'name': wh.name,
            'code': wh.code,
            'city': wh.partner_id.city or '',
            'pending': pending,
            'done_today': done_today,
            'overdue': overdue,
            'product_count': len(quants.mapped('product_id')),
            'total_qty': round(sum(quants.mapped('quantity')), 2),
            'low_stock_count': low_stock_count,
            'utilization': utilization,
            'lot_stock_id': wh.lot_stock_id.id,
        }

    def _build_summary(self, warehouses):
        Picking = self.env['stock.picking']
        now = fields.Datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0)
        return {
            'warehouse_count': len(warehouses),
            'total_pending': Picking.search_count([
                ('picking_type_id.warehouse_id', 'in', warehouses.ids),
                ('state', 'in', ('assigned', 'waiting', 'confirmed')),
            ]),
            'total_done_today': Picking.search_count([
                ('picking_type_id.warehouse_id', 'in', warehouses.ids),
                ('state', '=', 'done'),
                ('date_done', '>=', fields.Datetime.to_string(today_start)),
            ]),
            'total_overdue': Picking.search_count([
                ('picking_type_id.warehouse_id', 'in', warehouses.ids),
                ('state', 'not in', ('done', 'cancel')),
                ('scheduled_date', '<', now),
            ]),
            'total_products': len(self.env['stock.quant'].search([
                ('location_id.usage', '=', 'internal'),
                ('quantity', '>', 0),
            ]).mapped('product_id')),
        }

    def _get_top_movers(self, warehouses, limit=5):
        moves = self.env['stock.move'].search([
            ('picking_id.picking_type_id.warehouse_id', 'in', warehouses.ids),
            ('state', '=', 'done'),
            ('date', '>=', fields.Datetime.to_string(fields.Datetime.now() - timedelta(days=30))),
        ])
        product_qty = {}
        for move in moves:
            pid = move.product_id.id
            product_qty.setdefault(pid, {'name': move.product_id.display_name, 'qty': 0})
            product_qty[pid]['qty'] += move.quantity
        return sorted(product_qty.values(), key=lambda x: x['qty'], reverse=True)[:limit]

    def _get_low_stock_products(self, warehouses, limit=8):
        result = []
        for op in self.env['stock.warehouse.orderpoint'].search([('warehouse_id', 'in', warehouses.ids)]):
            if op.qty_on_hand <= op.product_min_qty:
                pct = min(round((op.qty_on_hand / op.product_max_qty) * 100, 0), 100) if op.product_max_qty > 0 else 0
                result.append({
                    'product': op.product_id.display_name,
                    'warehouse': op.warehouse_id.name,
                    'on_hand': round(op.qty_on_hand, 2),
                    'min_qty': round(op.product_min_qty, 2),
                    'pct': pct,
                })
        return sorted(result, key=lambda x: x['on_hand'])[:limit]

    def _get_recent_transfers(self, warehouses, limit=6):
        pickings = self.env['stock.picking'].search([
            ('picking_type_id.warehouse_id', 'in', warehouses.ids),
            ('state', '=', 'done'),
        ], order='date_done desc', limit=limit)
        return [{
            'name': p.name,
            'warehouse': p.picking_type_id.warehouse_id.name,
            'partner': p.partner_id.name or '',
            'date': p.date_done.strftime('%b %d, %H:%M') if p.date_done else '',
            'product_count': len(p.move_ids.mapped('product_id')),
        } for p in pickings]
