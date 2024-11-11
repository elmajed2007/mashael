# -*- coding: utf-8 -*-
from odoo import fields, models

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    salon_spa = fields.Boolean(string="Salon spa")