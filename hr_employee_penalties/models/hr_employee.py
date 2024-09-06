# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    penalty_line_ids = fields.One2many('hr.employee.penalty', 'employee_id')

    def _calculate_penalties(self, date_from, date_to):
        penalties = self.penalty_line_ids.search(
            [('date', '>=', date_from), ('date', '<=', date_to), ('state', '=', 'approved')])
        penalty_rule_lines = self.env['hr.penalty.policy.line'].search(
            [('id', 'in', penalties.mapped('rule_line_id.id'))])

        total = 0
        for penalty in penalty_rule_lines:
            count = len(penalties.filtered(lambda r: r.rule_line_id.id == penalty.id))

            if count == 1:
                total += penalty.first
            elif count == 2:
                total += penalty.first + penalty.second
            elif count == 3:
                total += penalty.first + penalty.second + penalty.third
            elif count == 4:
                total += penalty.first + penalty.second + penalty.third + penalty.fourth
            elif count == 5:
                total += penalty.first + penalty.second + penalty.third + penalty.fourth + penalty.fifth
            else:
                total += penalty.first + penalty.second + penalty.third + penalty.fourth + penalty.fifth + (
                        penalty.fifth * (count - 5))
        return total
