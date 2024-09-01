from odoo import fields, api, models
from datetime import date, datetime, time

from odoo.tests import users


class ResUser(models.Model):
    _inherit = 'res.users'

    loan_gurantee = fields.Boolean('Loan Gurantee')

class HREndService(models.Model):
    _inherit = 'hr.end.service.benefit'

    @api.model
    def _update_date(self):
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            if employees:
                esb_records = self.search([('employee_id', '=', employee.id)])
                today = date.today()
                for rec in esb_records:
                    if rec.employee_id and rec.date:
                        rec._compute_total_deserved_amount()
                        rec._compute_total_reward()
                        rec._compute_available_amount()
                        rec.date = today
                        rec.write({
                            'date': rec.date,
                            'total_deserved_amount': rec.total_deserved_amount,
                            'total_reward': rec.total_reward,
                            'available_amount': rec.available_amount,
                        })


class HRLoan(models.Model):
    _inherit = 'hr.loan'

    user_id = fields.Many2one('res.user', string='User')
    employee_ids = fields.Many2many('hr.employee', string='Employees', compute='_compute_emp', readonly=False)
    gurantee_id = fields.Many2one('hr.employee', string='Gurantee', domain="[('id', '=', employee_ids)]")
    gurante_id = fields.Many2one('hr.employee', string='Gurantee')


    parent_loan_id = fields.Many2one(
        comodel_name='hr.loan',
        string='Loan',
        required=False)

    hide_jurantee_field = fields.Boolean(string="Is Loan Check User", compute='_compute_hide_employee_field')

    @api.depends('loan_amount', 'date', 'employee_id')
    def _compute_emp(self):
        for rec in self:
            esb = rec.env['hr.end.service.benefit'].search([('date', '=', rec.date)])
            for record in esb:
                if record.type == 'ending_service':
                    if record.end_service_benefit_type_id.name == 'سلفة الموظف':
                        if record.total_reward > rec.loan_amount:
                            rec.employee_ids = [(4, record.employee_id.id)]

    @api.depends('gurante_id')
    def _compute_hide_employee_field(self):
        loan_gurantee_group = self.env.ref('mshaal.loan_gurantee_group_show')
        for rec in self:
            rec.hide_jurantee_field = self.env.user.id in loan_gurantee_group.users.ids


    def create_gurantee_rec(self):
        # Check if a related loan record already exists
        existing_loan = self.env['hr.loan'].search([
            ('parent_loan_id', '=', self.id),
            ('employee_id', '=', self.gurantee_id.id)
        ], limit=1)

        if existing_loan:
            # If the loan record already exists, open it instead of creating a new one
            return {
                'type': 'ir.actions.act_window',
                'name': 'Loan',
                'view_mode': 'form',
                'res_model': 'hr.loan',
                'res_id': existing_loan.id,
                'target': 'new',
            }

        # If no loan record exists, create a new one
        loan = self.env['hr.loan'].create({
            'name': self.name,
            'parent_loan_id': self.id,
            'employee_id': self.gurantee_id.id,
            'gurantee_id': self.employee_id.id,
            'currency_id': self.currency_id.id,
            'date': self.date,
            'loan_amount': self.loan_amount,
            'installment': self.installment,
            'payment_date': self.payment_date,
        })
        print('Loan created:', loan)

        # Create loan lines
        loan_lines = []
        for line in self.loan_line_ids:
            loan_lines.append((0, 0, {
                'date': line.date,
                'amount': line.amount,
                'paid': line.paid,
            }))
        loan.loan_line_ids = loan_lines
        print('Loan lines added:', loan.loan_line_ids)

        # Open the newly created loan record in form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loan',
            'view_mode': 'form',
            'res_model': 'hr.loan',
            'res_id': loan.id,
            'target': 'new',
        }

# def action_open_loan_list(self):
#     self.ensure_one()
#     action = self.env["ir.actions.actions"]._for_xml_id('ent_ohrms_loan.hr_loan_action')
#     action.update({'domain': [('employee_id', '=', self.employee_id.id)],
#                    'views': [[False, 'list'], [False, 'kanban'], [False, 'activity'], [False, 'form']],
#                    'context': {'default_employee_id': self.employee_id.id}})
#     return action
