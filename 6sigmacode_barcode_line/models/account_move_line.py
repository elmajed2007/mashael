from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'
    subj_ar = fields.Char(string="Arabic Subject")



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    barcode=fields.Char(string='Barcode',related="product_id.barcode",readonly=False)


