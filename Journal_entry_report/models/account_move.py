from odoo import models, fields, api, _
from odoo.tools import frozendict, format_date, float_compare, Query


class AccountMove(models.Model):
    _inherit = "account.move"

    today = fields.Date(default=fields.Date.context_today)
    total_credit = fields.Float('Total Credit', compute="compute_total")
    total_debit = fields.Float('Total Debit', compute="compute_total")

    def compute_total(self):
        t_d = 0
        t_c = 0
        for line in self.invoice_line_ids:
            t_d += line.debit
            t_c += line.credit

        self.total_credit = t_c
        self.total_debit = t_d
