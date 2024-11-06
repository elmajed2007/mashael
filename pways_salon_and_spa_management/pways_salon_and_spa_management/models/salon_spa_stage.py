from datetime import date, datetime
from odoo import api, fields, models

class SalonStage(models.Model):
    _name = 'salon.stage'
    _order = 'sequence'
    _description = 'Salon Stage'

    name = fields.Char(string="Name", required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")