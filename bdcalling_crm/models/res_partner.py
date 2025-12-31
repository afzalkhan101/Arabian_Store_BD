from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_employee = fields.Boolean(string="Is Employee")

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        if self.env.context.get('skip_lead_creation'):
            return partner
        Lead = self.env['crm.lead'].sudo()

        existing_lead = Lead.search([('partner_id', '=', partner.id)], limit=1)
        if existing_lead:
            _logger.info(
                "Lead already exists for partner %s (ID %s)",
                partner.name, partner.id
            )
            return partner

        lead_vals = {
            'name': partner.name or _('New Lead'),
            'partner_id': partner.id,
            'email_from': partner.email or False,
            'phone': partner.phone or False,
            'company_id': partner.company_id.id or self.env.company.id,
        }

        new_lead = Lead.create(lead_vals)

       
      
        sequence_code = 'crm.lead.serial'
        serial_number = self.env['ir.sequence'].next_by_code(sequence_code)
        if serial_number:
            new_lead.serial_number = serial_number
        else:
            new_lead.serial_number = f'{new_lead.id}'
        return partner


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    employee_name = fields.Many2one(
        'res.partner',
        string="Employee",
        domain=[('is_employee', '=', True)]
    )
    serial_number = fields.Char(string="Serial Number", readonly=True)
