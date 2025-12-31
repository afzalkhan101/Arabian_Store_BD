from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

class CustomAuthSignupHome(AuthSignupHome):

    @http.route(['/web/signup'], type='http', auth="public", website=True, methods=['POST','GET'])
    def web_auth_signup(self, *args, **kw):
        print("@@@@@@@@@@@@@2")
        phone = kw.get('phone')
        
        response = super(CustomAuthSignupHome, self).web_auth_signup(*args, **kw)

        if request.env.user and phone:
            request.env.user.sudo().partner_id.write({'phone': phone})

        return response
