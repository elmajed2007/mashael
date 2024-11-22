# -*- coding: utf-8 -*-
# from odoo import http


# class MshaeelPurchaseCustomize(http.Controller):
#     @http.route('/mshaeel_purchase_customize/mshaeel_purchase_customize', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mshaeel_purchase_customize/mshaeel_purchase_customize/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mshaeel_purchase_customize.listing', {
#             'root': '/mshaeel_purchase_customize/mshaeel_purchase_customize',
#             'objects': http.request.env['mshaeel_purchase_customize.mshaeel_purchase_customize'].search([]),
#         })

#     @http.route('/mshaeel_purchase_customize/mshaeel_purchase_customize/objects/<model("mshaeel_purchase_customize.mshaeel_purchase_customize"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mshaeel_purchase_customize.object', {
#             'object': obj
#         })

