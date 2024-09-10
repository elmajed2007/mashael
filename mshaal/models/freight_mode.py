from odoo import models, fields, api


class FreightMode(models.Model):
    _name = 'freight.mode'

    name = fields.Char(string='Name')
