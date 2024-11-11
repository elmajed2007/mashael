from odoo import api, models, fields, _
from datetime import date, timedelta, datetime
from odoo.exceptions import UserError, ValidationError, AccessError

class EmployeeWork(models.Model):
    _name = 'employee.work'
    _description = 'Employee Work'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    total_amount = fields.Float(string='Total Amount', compute="_compute_total_amount")
    total_orders = fields.Integer(string='Total Orders', compute="_compute_orders_amount")
    total_work_hours = fields.Integer(string='Total Time Worked', compute="_compute_total_hours")
    total_commission_amount = fields.Float(string='Total Commission Amount', compute="_compute_total_commission_amount")
    commission_to_pay = fields.Float(string='Commission To Pay', compute="_compute_commission_to_pay")
    # employee_id = fields.Many2one('res.users', string="Employee Name", readonly=1)
    employee_id = fields.Many2one('res.users', string="Employee Name")
    commission_rules_id = fields.Many2one('commission.rules')
    employee_work_lines_ids = fields.One2many("employee.work.lines", "employee_work_id", string="Employee Work Lines")
    salon_order_lines_ids = fields.One2many('salon.order.line', 'employee_work_id', string="Salon Order Lines")
    today_date = fields.Datetime(string="Today's Date", default=date.today())
    time_based = fields.Selection([("month","Month"), ("week","Week"),("today","Today")], default="month", string="Time")
    bills_count = fields.Integer(string="Bills", compute="_bill_count")

    @api.onchange("time_based")
    def _filter_records(self):
        if self.time_based == "today":
            print("Today called")
            today_date = self.today_date
            employye_work_lines = self.env['employee.work.lines'].search([('employee_id', '=', self.employee_id.id), ('date', '=', today_date)])
            if employye_work_lines:
                self.employee_work_lines_ids = employye_work_lines.ids
            else:
                self.employee_work_lines_ids = False

        if self.time_based == "month":
            print("month called")
            month_start_date = self.today_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = month_start_date.replace(day=28) + timedelta(days=4)
            month_end_date = next_month - timedelta(days=next_month.day, hours=1, minutes=0, seconds=0, microseconds=0)
            print("month_start_date.........", month_start_date)
            employye_work_lines = self.env['employee.work.lines'].search([('employee_id', '=', self.employee_id.id), ('date', '>=', month_start_date), ('date', '<=', month_end_date)])
            if employye_work_lines:
                self.employee_work_lines_ids = employye_work_lines.ids
            else:
                self.employee_work_lines_ids = False

        if self.time_based == "week":
            print("Week called")
            today = fields.Date.from_string(fields.Date.today())
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            employye_work_lines = self.env['employee.work.lines'].search([('employee_id', '=', self.employee_id.id), ('date', '>=', start_date), ('date', '<=', end_date)])
            if employye_work_lines:
                self.employee_work_lines_ids = employye_work_lines.ids
            else:
                self.employee_work_lines_ids = False

    @api.depends('employee_work_lines_ids')
    def _compute_total_commission_amount(self):
        total_commission_amount = 0
        if self.employee_work_lines_ids:
            for total in self.employee_work_lines_ids:
                total_commission_amount = total_commission_amount + total.commission_amount
        self.total_commission_amount = total_commission_amount

    @api.depends('employee_work_lines_ids')
    def _compute_total_amount(self):
        total_amount = 0
        if self.employee_work_lines_ids:
            for total in self.employee_work_lines_ids:
                total_amount = total_amount + total.price_subtotal
        self.total_amount = total_amount

    @api.depends('employee_work_lines_ids')
    def _compute_orders_amount(self):
        total_orders = []
        if self.employee_work_lines_ids:
            for total in self.employee_work_lines_ids:
                total_orders.append(total.id)
        lenth = len(total_orders)
        self.total_orders = lenth

    @api.depends('employee_work_lines_ids')
    def _compute_total_hours(self):
        total_hours = []
        if self.employee_work_lines_ids:
            for total in self.employee_work_lines_ids:
                total_hours.append(total.time_taken_total)
        hours = sum(total_hours)
        self.total_work_hours = hours

    @api.depends('employee_work_lines_ids.commission_paid')
    def _compute_commission_to_pay(self):
        to_pay = []
        amount = 0
        employee_work_lines = self.env['employee.work.lines'].search([('commission_paid',  '=', False), ("employee_id", "=", self.employee_id.id)])
        if employee_work_lines:
            for rec in employee_work_lines:
                to_pay.append(rec.commission_amount)
            amount = sum(to_pay)
        self.commission_to_pay = amount

    def pay_commission(self):
        to_pay = []
        amount = 0
        employee_work_lines = self.env['employee.work.lines'].search([('commission_paid',  '=', False), ("employee_id", "=", self.employee_id.id)])
        if employee_work_lines:
            for rec in employee_work_lines:
                if rec.commission_amount:
                    print("rec.commission_amount", rec.commission_amount)
                    vals = {
                            'name' : "Employee Commission",
                            'quantity':1,
                            'price_unit': rec.commission_amount,
                            }
                    rec.commission_paid = True
                    to_pay.append(vals) 
            print("Amount...........", to_pay)
            partner_id = self.env['res.partner'].search([('name' ,'=', self.employee_id.name)], limit=1)
            if to_pay:
                inv_id = self.env['account.move'].create({
                        'move_type':'in_invoice',
                        'partner_id': partner_id.id,
                        'invoice_date':self.today_date if self.today_date else datetime.datetime.today(),
                        'invoice_line_ids' : to_pay,
                        'salon_spa' : True,
                })
            else:
                raise ValidationError("You Can't Pay Invoice of 0.")

    def view_bills(self):
        partner_id = self.env['res.partner'].search([('name' ,'=', self.employee_id.name)], limit=1)
        action = self.env["ir.actions.actions"]._for_xml_id("pways_salon_and_spa_management.bill_salon_spa_form_action")
        action['domain'] = [('move_type', '=', 'in_invoice'), ('partner_id', '=', partner_id.id)]
        return action

    def _bill_count(self):
        partner_id = self.env['res.partner'].search([('name' ,'=', self.employee_id.name)], limit=1)
        bills = self.env['account.move'].search([('move_type', '=', 'in_invoice'), ('partner_id', '=', partner_id.id)])
        self.bills_count = len(bills)

class EmployeeWorkLines(models.Model):
    _name = 'employee.work.lines'
    _description = 'Employee Work Lines'
    _rec_name = 'employee_id'

    employee_work_id = fields.Many2one('employee.work', string="Employee Work")
    employee_id = fields.Many2one('res.users', string="Employee Name")
    date = fields.Datetime(string="Date")
    chair_id = fields.Many2one('salon.chair', string="Chair")
    partner_id = fields.Many2one('res.partner', string="Customer Name")
    product_id = fields.Many2one("product.product", string="Product")
    price_subtotal = fields.Monetary(string='Subtotal')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    commission_amount = fields.Float(string='Commission Amount')
    time_taken_total = fields.Float(string="Time")
    product_names = fields.Char(string="Product Name")
    commission_amount = fields.Float(string='Commission Amount', readonly=1)
    commission_paid = fields.Boolean(string="Commission Paid")

