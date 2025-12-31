{
    "name": "Bdcalling CRM Customization",
    "version": "1.0.0",
    "category": "Sales/CRM",
    "summary": "Custom CRM features for Bdcalling IT",
    "description": """Bdcalling CRM Customization

This module extends Odoo CRM with custom features for Bdcalling IT, including:
- Lead management enhancements
- Custom fields and views
- Automation support for lead creation
- Business-specific CRM workflows
""",
    "author": "Bdcalling IT",
    "website": "https://www.bdcalling.com",
    "license": "LGPL-3",
    "depends": ['base', 'crm'],
    "data": [
        "security/ir.model.access.csv",
        'views/res_partner.xml',
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}