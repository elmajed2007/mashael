from odoo import models, fields, api


class HsCode(models.Model):
    _name = 'hs.code'


    # name= fields.Integer('ID',required=True)
    name = fields.Char(
        string='ID',
        required=True)
    type_arabic_name= fields.Char('Product In Arabic')
    type_english_name=fields.Char('Product In English')
    duty_rate=fields.Float('Duty Rate')

class ProductTemplete(models.Model):
    _inherit = 'product.template'

    hs_code = fields.Many2one('hs.code',
        string="HS Code",
        help="Standardized code for international shipping and goods declaration. At the moment, only used for the FedEx shipping provider.",
    )