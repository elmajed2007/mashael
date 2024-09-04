from odoo import api, fields, models


class PoSerial(models.Model):
    _name = 'po.serial'
    _description = 'PO Serial'
    _rec_name = "name"

    name = fields.Char()

