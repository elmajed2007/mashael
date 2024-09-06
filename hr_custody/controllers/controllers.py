# -*- coding: utf-8 -*-
# from odoo import http


# class HrCustody(http.Controller):
#     @http.route('/hr_custody/hr_custody', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_custody/hr_custody/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_custody.listing', {
#             'root': '/hr_custody/hr_custody',
#             'objects': http.request.env['hr_custody.hr_custody'].search([]),
#         })

#     @http.route('/hr_custody/hr_custody/objects/<model("hr_custody.hr_custody"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_custody.object', {
#             'object': obj
#         })
