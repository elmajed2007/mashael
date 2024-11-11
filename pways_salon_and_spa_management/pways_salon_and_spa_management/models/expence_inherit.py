from odoo import fields, models

class HrExpenceInherit(models.Model):
    _inherit = "hr.expense"

    salon_spa = fields.Boolean(string="Salon spa")