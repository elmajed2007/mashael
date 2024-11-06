from odoo import api, models, fields, _
from datetime import date

class QatationInherit(models.Model):
    _inherit = "sale.order"

    is_salon_product = fields.Boolean(string="Salon Product")
    is_spa_product = fields.Boolean(string="Spa Product")