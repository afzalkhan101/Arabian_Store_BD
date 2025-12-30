from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class CustomWebsiteSale(http.Controller):

    @http.route(['/shop/cart/add'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_add(self, product_id=None, add_qty=1, **kwargs):
        """Custom Add-to-Cart route with CRM lead creation"""
        
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@",product_id)
        
        user = request.env.user
        if user and not user._is_public():
            request.env['crm.lead'].sudo().create({
                'name': f'Cart Add - {user.name}',
                'contact_name': user.name,
                'partner_id': user.partner_id.id,
                'phone': user.partner_id.phone,
                'email_from': user.email or '',
                'type': 'opportunity',
            })
            _logger.info("CRM Lead created for user %s", user.name)
    
   
        if product_id:
            try:
                product_id = int(product_id)
                sale_order = request.website.sale_get_order(force_create=True)
                product = request.env['product.product'].browse(product_id)

                if product.exists():
                    line = sale_order.order_line.filtered(lambda l: l.product_id.id == product.id)
                    if line:
                        line.write({'product_uom_qty': line.product_uom_qty + float(add_qty)})
                    else:
                        request.env['sale.order.line'].sudo().create({
                            'order_id': sale_order.id,
                            'product_id': product.id,
                            'product_uom_qty': float(add_qty),
                            'product_uom': product.uom_id.id,
                            'price_unit': product.lst_price,
                        })
                    _logger.info("Product %s added to cart successfully", product_id)
                else:
                    _logger.error("Product %s does not exist", product_id)
            except (ValueError, TypeError) as e:
                _logger.error("Error processing product_id: %s", e)
        else:
            _logger.warning("No product_id provided")

        return request.redirect(request.httprequest.referrer or '/shop')
    