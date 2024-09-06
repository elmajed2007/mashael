# -*- coding: utf-8 -*-

from odoo import models, fields


class HrJobInherit(models.Model):
    _inherit = "hr.job"

    arabic_name = fields.Char(string="Arabic Name")
