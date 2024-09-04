from odoo import api, fields, models


class PivSerial(models.Model):
    _name = 'piv.serial'
    _description = 'PivSerial'
    _rec_name = "name"

    name = fields.Char()

