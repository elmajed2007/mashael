# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    salon_spa = fields.Boolean(string="Salon spa")
    to_pay = fields.Float(string="Amount To pay")
    to_pay_product = fields.Char(string="Product To pay")
    not_to_pay_product = fields.Char(string="Product Not To Pay")
    not_to_pay = fields.Float(string="Amount Not To Pay")
    # is_salon_product = fields.Boolean(string="Salon Product")
    # is_spa_product = fields.Boolean(string="Spa Product")

