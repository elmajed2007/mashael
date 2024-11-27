# -*- coding: utf-8 -*-

from odoo import models, fields, api



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    date_of_arrival = fields.Date(
        string='Date Of Arrival',
        required=False)

    confirmation_no = fields.Char(
        string='Confirmation No',
        required=False)




class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    hs_code = fields.Many2one('hs.code', string="HS Code", related='product_id.product_tmpl_id.hs_code')



