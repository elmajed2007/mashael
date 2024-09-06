# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class hr_department(models.Model):
    _inherit = 'hr.department'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False)

    arabic_name = fields.Char(string="Arabic Name")