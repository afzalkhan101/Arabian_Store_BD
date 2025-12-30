from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)


class CustomWebsiteSale(WebsiteSale):
    """
    Extend WebsiteSale to add lead creation logic after cart operations.
    """

    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kwargs):
        """
        Override cart_update_json (AJAX cart additions).
        """
        _logger.info("=== cart_update_json called ===")
        _logger.info(f"Product ID: {product_id}, Add Qty: {add_qty}")
        
        # Call parent method first
        response = super().cart_update_json(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            display=display,
            **kwargs
        )
        
        # Create lead for logged-in users
        user = request.env.user
        _logger.info(f"User: {user.name}, Is Public: {user._is_public()}")
        
        if user and not user._is_public() and user.partner_id:
            try:
                lead = self._create_cart_lead(user)
                _logger.info(f"Lead creation result: {lead}")
            except Exception as e:
                _logger.error(f"Failed to create lead: {str(e)}", exc_info=True)
        
        return response

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """
        Override standard cart update route (form POST).
        This is often used by custom "Add to Cart" buttons.
        """
        _logger.info("=== cart_update (HTTP POST) called ===")
        _logger.info(f"Product ID: {product_id}, Add Qty: {add_qty}")
        
        # Call parent method
        response = super().cart_update(product_id=product_id, add_qty=add_qty, set_qty=set_qty, **kw)
        
        # Create lead
        user = request.env.user
        _logger.info(f"User: {user.name}, Is Public: {user._is_public()}")
        
        if user and not user._is_public() and user.partner_id:
            try:
                lead = self._create_cart_lead(user)
                _logger.info(f"Lead created: {lead.id if lead else 'Already exists'}")
            except Exception as e:
                _logger.error(f"Failed to create lead: {str(e)}", exc_info=True)
        
        return response

    def _create_cart_lead(self, user):
        """
        Helper method to create CRM lead for cart activity.
        """
        partner = user.partner_id
        
        _logger.info(f"Creating lead for partner: {partner.name} (ID: {partner.id})")
        
        # Check if opportunity already exists
        existing_lead = request.env['crm.lead'].sudo().search([
            ('partner_id', '=', partner.id),
            ('type', '=', 'opportunity'),
            ('probability', '<', 100)  # Not won
        ], limit=1)
        
        if existing_lead:
            _logger.info(f"Lead already exists: {existing_lead.id} - {existing_lead.name}")
            return existing_lead
        
        # Create new opportunity
        lead_vals = {
            'name': f'eCommerce Interest - {partner.name}',
            'contact_name': partner.name,
            'partner_id': partner.id,
            'phone': partner.phone or False,
            'email_from': partner.email or user.email or False,
            'type': 'opportunity',
            'description': 'Customer added product to shopping cart',
        }
        
        _logger.info(f"Creating new lead with vals: {lead_vals}")
        lead = request.env['crm.lead'].sudo().create(lead_vals)
        _logger.info(f"✓ Lead created successfully: ID {lead.id}")
        
        return lead