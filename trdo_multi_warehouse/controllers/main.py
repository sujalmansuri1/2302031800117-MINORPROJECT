from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class MultiWarehouseWebsiteSale(WebsiteSale):

    def _check_cart(self, order_sudo):
        redirection = super()._check_cart(order_sudo)
        if redirection:
            return redirection
        if order_sudo and not order_sudo._is_cart_ready():
            return request.redirect('/shop/cart')
