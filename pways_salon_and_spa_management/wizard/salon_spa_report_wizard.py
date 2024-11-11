from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, datetime

class SalonSpaReportWizard(models.TransientModel):
    _name = 'salon.spa.report.wizard'
    _description = "Salon Spa Report Wizard"

    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    report_of = fields.Selection([("income_report", "Income and Sales"), ('employee', "Employee"), ('customer', 'Customer')], default="income_report")
    employee_id = fields.Many2many('res.users', string="Employee")

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('To date must be greater than from date')

    def action_print_report(self):
        if self.report_of == "employee":
            employee = self.env['employee.work.lines'].search([('date', '>=', self.start_date), ('date', '<=', self.end_date), ('employee_id', 'in', self.employee_id.ids)])
            data = {
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'report_of' : self.report_of,
                    'employee': employee.ids,
                    } 
        elif self.report_of == "customer":
            customer_membership = self.env['membership.membership_line'].search([('date', '>=', self.start_date), ('date', '<=', self.end_date)])
            customer = self.env['employee.work.lines'].search([('date', '>=', self.start_date), ('date', '<=', self.end_date)])
            data = {
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'report_of' : self.report_of,
                    'customer_membership': customer_membership.ids,
                    'customer': customer.ids,
                    } 
        else:
            income_sales = self.env['employee.work.lines'].search([('date', '>=', self.start_date), ('date', '<=', self.end_date)])
            data = {
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'report_of' : self.report_of,
                    'income_sales': income_sales.ids,
                    }  
        print("Data...............", data)
        report = self.env.ref('pways_salon_and_spa_management.report_salon_spa_action')
        print("Report..........", report)
        return report.report_action(self, data=data)

    @api.onchange('report_of')
    def to_clear_value(self):
        self.employee_id = False
