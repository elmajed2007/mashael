# -*- coding: utf-8 -*-
import babel
import time
from datetime import datetime
from odoo import models, fields, api, tools, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class FinancialDeduct(models.Model):
    _name = "hr.financial.deduct"
    _description = "HR Financial Deduct"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "employee_id"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled')], string="Status", default="draft")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True)
    employee_no = fields.Char(related="employee_id.employee_no")
    emp_department_id = fields.Many2one(related="employee_id.department_id", string="Department")
    emp_job_id = fields.Many2one(related="employee_id.job_id", string="Job Position")
    date = fields.Date(string="Date", required=True, readonly=True)

    deduct_amount = fields.Float(string="Deduct Amount", required=True, readonly=True)
    reason = fields.Text(string="Reason", readonly=True)

    def action_confirm(self):
        self.write({'state': 'in_progress'})

    @api.constrains("date")
    def check_date(self):
        for rec in self:
            date = rec.date
            payslip = self.env['hr.payslip'].search([('employee_id', '=', rec.employee_id.id),
                                                     ('state', 'not in', ['dratf', 'verify']),
                                                     ('date_from', '<=', rec.date), ('date_to', '>=', rec.date)])
            if payslip:
                for i in payslip:
                    raise UserError(
                        _("Cannot make a deduction in this date, confirmed payslip is found: [ %s ] ") % (i.name))

    def action_approve(self):
        # add to payroll 
        self.write({'state': 'approve'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})
