from odoo import api, fields, models


class PricePolicy(models.Model):
    _name = 'price.policy'
    _description = 'Price Policy'
    _rec_name = 'name'

    name = fields.Char(string="Price Policy")
    destination_id = fields.Many2one(comodel_name='destination', string='Shipping Mode')
    description = fields.Char(string='Description', required=False)
    currency_exchange_top_up = fields.Float(string='Currency Exchange Top up', required=False)
    insurance = fields.Float(string='Insurance', required=False)
    over_head_factor = fields.Float(string='Over Head Factor', required=False)
    delivery = fields.Float(string='Delivery', required=False)
    red_price_factor = fields.Float(string='Red Price Factor', required=False)
    green_price_factor = fields.Float(string='Green Price Factor', required=False)
