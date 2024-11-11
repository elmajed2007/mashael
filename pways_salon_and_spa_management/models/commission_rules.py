from datetime import datetime, time
from odoo import api, fields, models, _

class Commission_Rules(models.Model):
    _name = 'commission.rules'
    _description = 'Commission Rules'

    name = fields.Char(string="Rule Name")
    target_price = fields.Float(string="Target Price")
    based_on = fields.Selection([('percentage', 'Percentage'),('fix','Fix')], default='percentage', string="Based On")
    percentage = fields.Float(string="Percentage")
    fix = fields.Float(string="Fix")
    is_salon_product = fields.Boolean(string="For Salon", default=True)
    is_spa_product = fields.Boolean(string="For Spa")
    
    @api.onchange('based_on')
    def clear_values(self):
        if self.based_on == 'percentage':
            if self.fix:
                self.fix = False
        if self.based_on == 'fix':
            if self.percentage:
                self.percentage = False

