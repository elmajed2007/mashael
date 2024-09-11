from odoo import api, fields, models



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    deal_id = fields.Many2one(comodel_name='msh.deal', string='Deal', required=False)

