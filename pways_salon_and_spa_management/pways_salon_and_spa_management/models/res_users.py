# -*- coding: utf-8 -*-
from odoo import fields, models

class Users(models.Model):
    _inherit = 'res.users'

    user_salon_active = fields.Boolean(string="Active Salon Users", default=False)
