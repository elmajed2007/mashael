from odoo import api, fields, models



class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_type = fields.Selection(
        string='Credit Type',
        selection=[('advanced', 'Advanced'),
                   ('credit_limit', 'Credit Limit'),
                   ('credit_limit_in_days', 'Credit Limit In Days'),
                   ],
        required=False, )

