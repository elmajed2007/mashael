# -*- coding: utf-8 -*-

from odoo import fields, models, _


class HrEmployeePenaltyInherit(models.Model):
    _inherit = 'hr.employee.penalty'

    def action_approve(self):
        records = self.filtered(lambda r: r.state == 'submit')
        records.write({'state': 'approved'})

        # Trigger penalty calculation
        for record in records:
            # Assuming you want to calculate penalties for the current month  that means durations 30 days
            date_from = record.date.replace(day=1).strftime('%Y-%m-%d')
            date_to = record.date.strftime('%Y-%m-%d')

            # Call the penalty calculation method in hr.employee
            total_penalty = record.employee_id._calculate_penalties(date_from, date_to)

            # Log or apply the penalty (depends on how you want to apply this in the system, e.g., deduction in salary)
            record.memo = f'Penalty of {total_penalty}% applied for the period from {date_from} to {date_to}.'
