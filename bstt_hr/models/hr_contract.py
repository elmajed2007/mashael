# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime


class HrContract(models.Model):
    _inherit = "hr.contract"

    ref = fields.Char('Reference', readonly=True, copy=False)
    employee_no = fields.Char(related="employee_id.employee_no", string='Employee Number', readonly=True, store=True)

    contract_duration = fields.Char(compute='_compute_duration')
    car_allowance = fields.Float(string="Travel Allowance", copy=False, tracking=True, )
    overtime_allowance = fields.Float(string="Overtime", copy=False, tracking=True, )
    food_allowance = fields.Float(string="Food Allowance", copy=False, tracking=True)
    housing_allowance = fields.Float(string="Housing", copy=False, tracking=True)
    mobile_allowance = fields.Float(string="Mobile", copy=False, tracking=True)
    fuel_allowance = fields.Float(string="Fuel Allowance", copy=False, tracking=True)
    ticket_allowance = fields.Float(string="Ticket Allowance", copy=False, tracking=True)
    commission_allowance = fields.Float(string='Nature of work Allowance', copy=False, tracking=True)
    other_financial_allowances = fields.Float(string=' Other Financial Allowance', copy=False, tracking=True)
    other_commission_allowance = fields.Float(string=' Commission Allowance', copy=False, tracking=True)

    other_allowance = fields.Float(string='Other', copy=False, tracking=True)

    work_permit_fees_deduction = fields.Float(string="Work Permit Fees", copy=False, tracking=True)
    leave_deduction = fields.Float(string="Leave", copy=False, tracking=True)
    esob_deduction = fields.Float(string="End Of Service (ESOB)", copy=False, tracking=True)
    tax_deduction = fields.Float(string="Taxes", copy=False, tracking=True)
    tax_deduction_amount = fields.Float(string="Taxes Amount", copy=False, tracking=True)

    iqama_fees_deduction = fields.Float(string="IQAMA Fees", copy=False, tracking=True)

    gosi_deduction = fields.Float(string="GOSI", copy=False, tracking=True, compute="_compute_gosi_amount", store=True)
    gosi_type = fields.Selection([
        ('national', 'National'),
        ('foreign', 'Foreign'),
        ('none', 'None')
    ], required=True, string='GOSI Type', index=True, tracking=True)
    gosi_percent = fields.Float(string="GOSI percent", copy=False, tracking=True, compute='_compute_gosi_percent')

    medical_insurance_deduction = fields.Float(string="Medical Insurance", copy=False, tracking=True)
    medical_insurance_family_deduction = fields.Float(string="Medical Insurance Family", copy=False, tracking=True)
    medical_insurance_type_id = fields.Many2one("hr.medical.insurance.type", string="Medical Insurance Type",
                                                copy=False, tracking=True)
    wage_day = fields.Float(string="Wage(Day)", copy=False, tracking=True, compute='_compute_daily_wage')
    # gross_wage = fields.Float(string="Gross", copy=False, tracking=True, compute='_compute_all_total')
    gross_wage = fields.Float(string="Gross", copy=False, tracking=True, compute='_compute_gross_wage')

    allowance_total = fields.Float(compute='_compute_all_total', store=True)
    service_year = fields.Float(string="Number of years working in company", compute='_compute_total_service_year',
                                store=True)

    travel_from_country = fields.Many2one('res.country', string='From', copy=False, tracking=True)
    travel_to_country = fields.Many2one('res.country', string='To', copy=False, tracking=True)
    travel_value = fields.Float(string='Value of Travel Allowance', copy=False, tracking=True)

    house_allowance_months = fields.Integer(string='Number of months housing allowance', tracking=True, default=1,
                                            help="يكتب هنا عدد الاشهر التي يصرف فيها بدل السكن")
    house_allowance_last_date = fields.Date(string='Last Month of housing allowance')

    contract_signature_date = fields.Date(string='Date Of Signing Contract')
    probation_period = fields.Integer(string="Trial period (days)")
    add_value = fields.Float(string='Diduct Value', copy=False, tracking=True)
    subtract_value = fields.Float(string='Add value', copy=False, tracking=True)

    external_house_allowance = fields.Float(string='External housing allowance')

    department_id = fields.Many2one('hr.department', compute='_compute_employee_contract', store=True, readonly=False,
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                    string="Department",
                                    related='employee_id.department_id')

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          related='employee_id.department_id.analytic_account_id',
                                          string='Analytic Account',
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    ticket_allowence = fields.Float(string="Ticket Allowence")

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('hr.contract')
        return super(HrContract, self).create(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('name', operator, name), ('ref', operator, name)] + args
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    @api.depends('wage', 'car_allowance', 'food_allowance', 'housing_allowance',
                 'mobile_allowance', 'fuel_allowance', 'ticket_allowance', 'commission_allowance', 'other_allowance',
                 'other_financial_allowances', 'other_commission_allowance')
    # def _compute_all_total(self):
    #     for cont in self:
    #         total = cont.car_allowance + cont.food_allowance + cont.housing_allowance + cont.mobile_allowance + cont.fuel_allowance + cont.ticket_allowance + cont.commission_allowance + cont.other_allowance + cont.other_financial_allowances + cont.other_commission_allowance
    #         cont.allowance_total = total
    #         cont.gross_wage = total + cont.wage

    def _compute_all_total(self):
        for cont in self:
            total = (cont.car_allowance + cont.food_allowance + cont.housing_allowance +
                     cont.mobile_allowance + cont.fuel_allowance + cont.ticket_allowance +
                     cont.commission_allowance + cont.other_allowance +
                     cont.other_financial_allowances + cont.other_commission_allowance)
            cont.allowance_total = total

    def _compute_gross_wage(self):
        for cont in self:
            cont.gross_wage = cont.allowance_total + cont.wage

    @api.depends('gosi_percent', 'wage', 'housing_allowance')
    def _compute_gosi_amount(self):
        for contract in self:
            gosi_deduction = 0.0
            if contract.gosi_percent and contract.wage:
                gosi_deduction = (contract.wage + contract.housing_allowance) * contract.gosi_percent
            contract.gosi_deduction = gosi_deduction

    @api.onchange('tax_deduction', 'wage')
    def _onchange_tax_deduction_amount(self):
        for contract in self:
            tax_amount = 0.0
            if contract.tax_deduction and contract.wage:
                tax_amount = contract.wage * contract.tax_deduction
            contract.tax_deduction_amount = tax_amount

    @api.onchange('medical_insurance_type_id')
    def _onchange_medical_insurance_amount(self):
        self.medical_insurance_deduction = self.medical_insurance_type_id and self.medical_insurance_type_id.amount or 0.0

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for contract in self:
            difference_in_years = relativedelta(contract.date_end, contract.date_start).years
            difference_in_months = relativedelta(contract.date_end, contract.date_start).months
            difference_in_days = relativedelta(contract.date_end, contract.date_start).days

            self.contract_duration = str(difference_in_years) + " سنة/سنوات " + " - " + str(
                difference_in_months) + " شهور " + " - " + str(difference_in_days) + " أيام"

    @api.depends('wage')
    def _compute_daily_wage(self):
        for contract in self:
            contract.wage_day = float(contract.wage / 30)

    @api.depends('gosi_type')
    def _compute_gosi_percent(self):
        for contract in self:
            if contract.gosi_type == 'national':
                contract.gosi_percent = 22 / 100
            else:
                contract.gosi_percent = 2 / 100

    @api.depends("date_start")
    def _compute_total_service_year(self):
        for rec in self:
            today = datetime.date.today()
            years = relativedelta(today, rec.date_start).years
            rec.service_year = years

    def notify_users(self):
        for rec in self:
            users = self.env['res.users'].search([])
            try:
                for user in users:
                    if user.has_group('bstt_hr.group_hr_employee_group'):
                        activity = self.env['mail.activity'].sudo().create({
                            'res_model_id': self.env.ref('bstt_hr.model_hr_contract').id,
                            'res_id': rec.id,
                            'activity_type_id': self.env.ref('bstt_hr.mail_activity_process_probation_period').id,
                            'user_id': user.id, })
            except:
                pass

    def calculate_probation_period(self):
        for rec in self.env['hr.contract'].sudo().search([('state', '=', 'open')]):
            if rec.probation_period:
                period = rec.probation_period
                notify_period = period - 30  # todo: better config
                today = datetime.date.today()
                start = rec.date_start
                difference_in_days = relativedelta(today, start).days
                if difference_in_days == notify_period:
                    rec.notify_users()


class ContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          related='contract_id.analytic_account_id')
    # department_id = fields.Many2one('hr.department', string='Department', readonly=True, related='contract_id.department_id', store=True)
