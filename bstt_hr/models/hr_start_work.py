#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EmployeeStartWork(models.Model):
    _name = 'hr.employee.start.work'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Start Work'

    name = fields.Char('Name', required=True)
    guidance = fields.Char('التوجيه')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, string="Company")
    employee_no = fields.Char(related="employee_id.employee_no", string='Employee No', readonly=True, store=True)
    start_work_date = fields.Date(string='Start Work Date', required=True)
    start_work_type = fields.Selection([('first', 'Start the job for the first time / appointed or transferred'),
                                        ('after_annual_holiday', 'Started work after annual leave'),
                                        ('after_sick_holiday', 'Start work after sick leave'),
                                        ('after_exceptional_holiday', 'Started working after an emergency leave'),
                                        ('after_education', 'Started working after a training/study course'),
                                        ('after_task', 'Start work after completing a task/assignment')],
                                       string='Start Work Type', required=True, copy=False)
    work_action_type = fields.Selection([('exemption', 'Exemption from any decision'),
                                         ('draw_attention', 'Notice to the employee'),
                                         ('deduct_from_salary',
                                          'Deduction of the number of days exceeded from the salary'),
                                         ('deduct_from_holiday',
                                          'Deduct the number of days exceeded from the next annual leave')
                                         ],
                                        string='Actions taken in case of violation', required=True, copy=False)

    job_id = fields.Many2one(related='employee_id.job_id', string='Job Position', store=True, readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True, readonly=True)
    project_id = fields.Many2one(related='employee_id.work_location_id.project_id', string='Project', store=True,
                                 readonly=True)
    # wage = fields.Monetary(related='employee_id.contract_id.wage', string='الراتب', store=True, readonly=True)
    is_project_manager = fields.Boolean(compute="is_project_manager_chk", default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('project_manager', 'Department Manager'),
        ('hr_manager', 'HR Manager'),
        ('executive_manager', 'Executive Manager'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancel'),
    ], string="State", default='draft', tracking=True, copy=False)

    def is_project_manager_chk(self):
        for rec in self:
            rec.is_project_manager = False
            # if self.env.user.id == rec.project_id.user_id.id or self.env.user.has_group('bstt_hr.group_project_manager_exceptional'):
            if self.env.user.id == rec.employee_id.parent_id.user_id.id:
                rec.is_project_manager = True

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_project_manager(self):
        self.write({'state': 'project_manager'})
        self.activity_schedule('mail.mail_activity_data_todo', user_id=self.employee_id.parent_id.id)

    def action_hr_manager(self):
        self.write({'state': 'hr_manager'})
        self.activity_feedback(['mail.mail_activity_data_todo'])
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('bstt_hr.group_hr_manager_group'):
                # self.add_follower_id(self.id, user.partner_id)
                self.activity_schedule('mail.mail_activity_data_todo', user_id=user.id)

    def action_executive_manager(self):
        self.write({'state': 'executive_manager'})
        self.activity_feedback(['mail.mail_activity_data_todo'])
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('bstt_hr.group_executive_manager'):
                # self.add_follower_id(self.id, user.partner_id)
                self.activity_schedule('mail.mail_activity_data_todo', user_id=user.id)

    def action_fast_approve(self):
        self.activity_feedback(['mail.mail_activity_data_todo'])
        self.write({'state': 'approve'})

    def action_approve(self):
        self.activity_feedback(['mail.mail_activity_data_todo'])
        self.write({'state': 'approve'})

    @api.model
    def create(self, vals):
        if vals.get('employee_id'):
            employee_count = self.env['hr.employee.start.work'].search_count([
                ('employee_id', '=', vals['employee_id']), ('state', 'not in', ['approve', 'refuse', 'cancel'])])
            if employee_count > 0:
                raise UserError(
                    _("It is not possible to create a request directly because there is a request under the procedure"))

        obj = super(EmployeeStartWork, self).create(vals)
        return obj

    # def unlink(self):
    #     if self.filtered('state') == 'approve':
    #         raise UserError(_('لايمكن حذف طلب مباشرة العمل في حالة الموافقة'))
    #     super(EmployeeStartWork, self).unlink()
    #     return True
