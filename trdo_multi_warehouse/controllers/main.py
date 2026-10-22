from odoo import http
from odoo.http import request


class WarehouseDashboardController(http.Controller):

    @http.route('/trdo/warehouse/dashboard', type='json', auth='user')
    def get_dashboard(self):
        return request.env['trdo.warehouse.dashboard'].get_dashboard_data()

    @http.route('/trdo/warehouse/cart_delivery', type='json', auth='user')
    def get_cart_delivery(self, order_id=None):
        if not order_id:
            order = request.env['sale.order'].sudo().search([
                ('website_id', '=', request.website.id),
                ('partner_id', '=', request.env.user.partner_id.id),
                ('state', '=', 'draft'),
            ], limit=1)
        else:
            order = request.env['sale.order'].sudo().browse(order_id)
        if not order:
            return {}
        return order._get_warehouse_delivery_estimate()
