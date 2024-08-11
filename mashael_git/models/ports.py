from odoo import api, fields, models


class MshPort(models.Model):
    _name = 'msh.port'
    _description = 'Ports'
    _rec_name = "name"

    name = fields.Char()


