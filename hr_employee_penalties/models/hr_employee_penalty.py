# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class HrEmployeePenalty(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'hr.employee.penalty'
    _description = 'Hr Employee Penalties'
    _check_company_auto = True

    rule_line_id = fields.Many2one('hr.penalty.policy.line', 'Description', required=True,
                                   tracking=True,
                                   readonly=True

                                   )
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('submit', 'Submit'),
        ('approved', 'Approved'),
    ], string='Status', readonly=True, tracking=True, copy=False, default='draft')
    date = fields.Date(
        index=True, copy=False,
        default=fields.Date.context_today,
        readonly=True,

        tracking=True, required=True)
    employee_id = fields.Many2one(
        'hr.employee', tracking=True,
        readonly=True,

        required=True)
    memo = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_submit(self):
        records = self.filtered(lambda r: r.state == 'draft')
        records.write({'state': 'submit'})

    def action_approve(self):
        records = self.filtered(lambda r: r.state == 'submit')
        records.write({'state': 'approved'})

        # Trigger penalty calculation
        for record in records:
            # Assuming you want to calculate penalties for the current month i.e means durations 30 days
            date_from = record.date.replace(day=1).strftime('%Y-%m-%d')
            date_to = record.date.strftime('%Y-%m-%d')

            # Call the penalty calculation method in hr.employee
            total_penalty = record.employee_id._calculate_penalties(date_from, date_to)

            # Log or apply the penalty (depends on how you want to apply this in the system, e.g., deduction in salary)
            record.memo = f'Penalty of {total_penalty}% applied for the period from {date_from} to {date_to}.'

    def action_cancel(self):
        self.filtered(lambda r: r.state in ['submit', 'draft']).write({'state': 'cancel'})

    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise UserError(_("You can't delete it in this state"))
        return super().unlink()
