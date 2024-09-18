from odoo import api, fields, models



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_type = fields.Selection(string='Price Type', selection=[('price_policy', 'Price Policy'), ('manual', 'Manual')], required=False)
    price_policy_id = fields.Many2one(comodel_name='price.policy', string='Price Policy', required=False)
    red_sales_price = fields.Float(string='Red Sales Price', required=False)
    green_sales_price = fields.Float(string='Green Sales Price', required=False)

