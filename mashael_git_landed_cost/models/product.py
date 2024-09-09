from odoo import api, fields, models



class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_glc_product = fields.Boolean(
        string='GLC Product',
        required=False)
