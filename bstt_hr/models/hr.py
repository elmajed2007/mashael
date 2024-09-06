#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from odoo.exceptions import UserError, Warning
from odoo.exceptions import UserError
import datetime
from datetime import date
from dateutil import relativedelta
import re
from odoo.exceptions import ValidationError
from stdnum import iban
from ummalqura.hijri_date import HijriDate


class Employee(models.Model):
    _inherit = "hr.employee"

    emp_type = fields.Selection([
        ('national', 'National'),  # مواطن
        ('displaced_tribes', 'Displaced Tribes'),  # قبائل نازحة
        ('citizen_son', 'Citizen Son'),  # ابن مواطن
        ('foreign', 'Resident'),  # مقيم
        ('citizen_wife', 'Citizen Wife'),  # زوجة مواطن
        ('citizen_husband', 'Citizen Husbund'),  # زوج مواطنة
    ], string='Type', index=True, tracking=True)
    # freelance = fields.Boolean(string ='Freelance',help="Use in Payslip calculation if it is True it will be not select in journal entry and if it is False it will selected in journal entry")
    foreign_name = fields.Char(string="Name in English", copy=False, tracking=True)
    sponsor = fields.Char(string="Sponsor", copy=False)
    employee_no = fields.Char(string='Employee Number', required=True, default=lambda self: _(''))
    iqama_job = fields.Char(string='Iqama Job', groups="hr.group_hr_user")
    manager_phone = fields.Char(string='Manager Phone', groups="hr.group_hr_user")
    age = fields.Integer(string='Age', compute='_compute_employee_age', groups="hr.group_hr_user")
    identification_id = fields.Char(string='ID Number/ Iqama', groups="hr.group_hr_user", tracking=True)
    iqama_expiry_date_hijri = fields.Char(string='Iqama Expiry Date(Higry)', compute='_get_iqama_expiry_date_hijri')
    # insurance_duration = fields.Selection(string="Insurance Duration",
    #                                       selection=[('day', 'Day'), ('month', 'Month'),('year', 'Year') ],
    #                                       )
    insurance_quantity = fields.Integer(string="Insurance Quantity")
    id_start_date = fields.Date(
        string='Issue Date',
        help='Start date of Identification ID')
    id_expiry_date = fields.Date(
        string='Expiry Date',
        help='Expiry date of Identification ID')

    iqama_date_da = fields.Date(string="Birth date in iqama")
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", groups="hr.group_hr_user",
                                       tracking=True)
    id_attachment_id = fields.Many2many(
        'ir.attachment', 'id_attachment_rel',
        'id_ref', 'attach_ref',
        string="ID Attachment",
        help='You can attach the copy of your Id')
    passport_expiry_date = fields.Date(
        string='Expiry Date',
        help='Expiry date of Passport ID')
    passport_start_date = fields.Date(
        string='Issue Date',
        help='ٍStart date of Passport ID')
    passport_attachment_id = fields.Many2many(
        'ir.attachment',
        'passport_attachment_rel',
        'passport_ref', 'attach_ref1',
        string="Passport Attachement",
        help='You can attach the copy of Passport')

    fam_ids = fields.One2many(
        'hr.employee.family', 'employee_id',
        string='Family Information', help='Family Information')
    ins_fam_ids = fields.One2many('hr.employee.family', related='fam_ids', string='Insurance Family Information',
                                  store_true=True, readonly=False)
    certificate_id = fields.Many2one('hr.certificates', string='Certification Level')
    # bank_account_id = fields.Many2one(
    #     'res.partner.bank', 'Bank Account Number',
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    #     groups="hr.group_hr_user",
    #     tracking=True,
    #     help='Employee bank salary account')
    start_work_request_count = fields.Integer(compute="_start_work_request_count")

    bank_account_no = fields.Char(string="Bank Account Number")
    bank_id = bank_id = fields.Many2one('res.bank', string="Bank")
    address = fields.Char(string="Address")

    """Start Insurance fields"""
    iqama = fields.Char(string="Iqama")
    iqama_duration = fields.Integer(string="Iqama Duration")
    medical_insurance_type_id = fields.Many2one("hr.medical.insurance.type", string="Medical Insurance Type",
                                                copy=False,
                                                tracking=True)
    medical_insurance_value = fields.Float(string="Insurance Amount", copy=False, tracking=True)
    medical_insurance_duration = fields.Integer(string="Insurance Duration", copy=False, tracking=True)
    medical_insurance_expire_date = fields.Date(string="Insurance Expiry Date", copy=False, tracking=True)
    medical_insurance_company = fields.Char(string="Insurance Company", copy=False, tracking=True)
    medical_insurance_life_partner = fields.Float(string="Insurance Ammount for Wife/Husband", copy=False,
                                                  tracking=True)
    medical_insurance_son1 = fields.Float(string="Insurance Ammount for Child1", copy=False, tracking=True)
    medical_insurance_son2 = fields.Float(string="Insurance Ammount for Child2", copy=False, tracking=True)
    medical_insurance_son3 = fields.Float(string="Insurance Ammount for Child3", copy=False, tracking=True)
    medical_insurance_son4 = fields.Float(string="Insurance Ammount for Child4", copy=False, tracking=True)
    medical_insurance_son5 = fields.Float(string="Insurance Ammount for Child5", copy=False, tracking=True)
    medical_insurance_son6 = fields.Float(string="Insurance Ammount for Child6", copy=False, tracking=True)
    medical_insurance_son7 = fields.Float(string="Insurance Ammount for Child7", copy=False, tracking=True)
    medical_insurance_son8 = fields.Float(string="Insurance Ammount for Child8", copy=False, tracking=True)
    medical_insurance_son9 = fields.Float(string="Insurance Ammount for Child9", copy=False, tracking=True)
    medical_insurance_son10 = fields.Float(string="Insurance Ammount for Child10", copy=False, tracking=True)
    """End Insurance fields"""

    nationality_ar = fields.Char(string='Arabic Nationality', help="used for report purpose")
    sick_timeoff_duration = fields.Float(string='Sick Timeoff Duration')
    paid_amount_before = fields.Float(string='Prepaid Amount')

    work_license_fee = fields.Float(string='Work Permit Fee')
    authority_license_fee = fields.Float(string='Authority License Fee')
    iqama_fee = fields.Float(string='Iqama Fees')
    other_fee_ids = fields.One2many('other.fees', 'employee_id', string="Other Fees")
    financial_deduct_ids = fields.One2many('hr.financial.deduct', 'employee_id', string="Fiscal Deficit")
    # new fields for insurance to be computed
    insurance_duration = fields.Char(string="Insurance Duration", copy=False, tracking=True,
                                     compute="medical_insurance_term")
    insurance_expire_date = fields.Date(string="Insurance Expiry Date", copy=False, tracking=True,
                                        compute="medical_insurance_term")
    insurance_company = fields.Char(string="Insurance Company", copy=False, tracking=True,
                                    compute="medical_insurance_term")
    payment_type = fields.Selection(string="Payment Type", selection=[('transfer', 'Transfer'), ('cash', 'Cash'), ])

    def medical_insurance_term(self):
        insurance_terms = self.env['hr.insurance.terms'].search([('active', '=', True)], limit=1)
        for employee in self:
            employee.insurance_duration = 0
            date_start = employee.contract_id.date_start
            if insurance_terms:
                employee.insurance_expire_date = insurance_terms.expire_date
                employee.insurance_company = insurance_terms.insurance_company
                difference_in_years = relativedelta.relativedelta(insurance_terms.expire_date, date_start).years
                difference_in_months = relativedelta.relativedelta(insurance_terms.expire_date, date_start).months
                difference_in_days = relativedelta.relativedelta(insurance_terms.expire_date, date_start).days
                if difference_in_years > 0:
                    employee.insurance_duration = str(difference_in_years) + " years" + " - " + str(
                        difference_in_months) + " months " + " - " + str(difference_in_days) + " days"
                else:
                    if difference_in_months > 0:
                        employee.insurance_duration = str(difference_in_months) + " months " + " - " + str(
                            difference_in_days) + " days"
                    else:
                        if difference_in_days > 0:
                            employee.insurance_duration = str(difference_in_days) + " days"
                        else:
                            employee.insurance_duration = False

            else:
                employee.insurance_expire_date = False
                employee.insurance_company = False

    @api.depends('id_expiry_date')
    def _get_iqama_expiry_date_hijri(self):
        for rec in self:
            rec.iqama_expiry_date_hijri = ''
            if rec.id_expiry_date:
                date = fields.Date.from_string(self.id_expiry_date)
                hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
                print(hijri_date, "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", int(hijri_date.year), int(hijri_date.month),
                      int(hijri_date.day))
                rec.iqama_expiry_date_hijri = str(hijri_date.day) + "-" + str(hijri_date.month) + "-" + str(
                    hijri_date.year)
                # rec.iqama_expiry_date_hijri=iqama_expiry_date_hijri + "هـ"

    def get_deduction_amount(self, date_to, date_from):
        for rec in self:
            amount = 0.0
            records = rec.financial_deduct_ids.filtered(
                lambda r: r.state == 'approve' and r.date >= date_from and r.date <= date_to)
            if records:
                for i in records:
                    amount += i.deduct_amount
            return amount

    @api.model
    def create(self, vals):
        if vals.get('employee_no', _('')) == _(''):
            vals['employee_no'] = self.env['ir.sequence'].next_by_code(
                'hr.employee') or _('')

        emp = super(Employee, self).create(vals)
        if vals.get('bank_account_no', False) or vals.get('bank_id', False) or vals.get('address', False):
            partner = self.env['res.partner'].create(
                {'name': emp.name,
                 'street': emp.address or False,
                 })
            emp.address_home_id = partner.id
            if emp.address_home_id and 'bank_account_no' in vals:
                res_partner_bank = self.env['res.partner.bank'].search([('acc_number', '=', vals['bank_account_no'])],
                                                                       limit=1)
                if res_partner_bank.partner_id.id and res_partner_bank.partner_id.id != emp.address_home_id.id:
                    raise UserError(
                        _("The bank account number must be unique. The bank account number registered in the name of %s",
                          res_partner_bank.partner_id.name))
                elif res_partner_bank.partner_id.id == emp.address_home_id.id:
                    emp.bank_account_id = res_partner_bank.id
                else:
                    emp.bank_account_id = self.env['res.partner.bank'].create({
                        'acc_number': emp.bank_account_no,
                        'bank_id': vals.get('bank_id', False),
                        'company_id': self.env.company.id,
                        # 'currency_id': self.currency_id.id,
                        'partner_id': emp.address_home_id.id,
                    }).id
        return emp

    def write(self, vals):
        if vals.get('bank_account_no', False) or vals.get('bank_id', False) or vals.get('address', False):
            for rec in self:
                if not rec.address_home_id:
                    partner = self.env['res.partner'].create(
                        {'name': rec.name or vals.get('name', False),
                         'street': vals.get('address', False),
                         })
                    rec.address_home_id = partner.id

                if rec.address_home_id and vals.get('address', False):
                    rec.address_home_id.street = vals.get('address', False)

                if rec.address_home_id and 'bank_account_no' in vals:
                    res_partner_bank = self.env['res.partner.bank'].search(
                        [('acc_number', '=', vals['bank_account_no'])], limit=1)
                    if res_partner_bank.partner_id.id and res_partner_bank.partner_id.id != rec.address_home_id.id:
                        raise UserError(
                            _("The bank account number must be unique. The bank account number registered in the name of %s",
                              res_partner_bank.partner_id.name))
                    elif res_partner_bank.partner_id.id == rec.address_home_id.id:
                        rec.bank_account_id = res_partner_bank.id
                    else:
                        rec.bank_account_id = self.env['res.partner.bank'].create({
                            'acc_number': vals.get('bank_account_no', False),
                            'bank_id': vals.get('bank_id', False),
                            'company_id': self.env.company.id,
                            # 'currency_id': self.currency_id.id,
                            'partner_id': rec.address_home_id.id,
                        }).id
        return super().write(vals)

    @api.onchange('identification_id')
    def _onchange_identification_id(self):
        if self.identification_id:
            self.identification_id = re.sub('[^0-9]', '', self.identification_id)
            if len(str(self.identification_id)) != 10:
                raise ValidationError(_("ID/Iqama number must be 10 digits"))

    def _start_work_request_count(self):
        for employee in self:
            req = self.env['hr.employee.start.work'].sudo().search([('employee_id', '=', employee.id)])
            employee.start_work_request_count = len(req)

    @api.depends('birthday')
    def _compute_employee_age(self):
        age = False
        if self.birthday:
            dob = self.birthday
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        self.age = age

    def action_create_start_work(self):
        """Create the Start Work.
        """
        employee_start_work_count = self.env['hr.employee.start.work'].search_count([
            ('employee_id', '=', self.id), ('state', 'not in', ['approve', 'refuse', 'cancel'])])
        if employee_start_work_count > 0:
            raise UserError(
                _("It is not possible to create a request directly because there is another request under the procedure"))

        action = {
            'name': _('Start Work'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.start.work',
            'context': {"default_employee_id": self.id, },
            'view_mode': 'form',
            'views': [[self.env.ref('bstt_hr.hr_start_work_form_view').id, 'form']],
        }
        return action

    def open_start_work_requests(self):
        self.ensure_one()
        req = self.env['hr.employee.start.work'].sudo().search([('employee_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'طلبات مباشرة العمل',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee.start.work',
            'domain': [('id', 'in', req.ids)]
        }

    # def _format_iban(self, bank_account_no):
    #     '''
    #     This function removes all characters from given 'string' that isn't a alpha numeric and converts it to upper case, checks checksums and groups by 4
    #     '''
    #     res = ''
    #     if bank_account_no:
    #         # _logger = logging.getLogger(__name__)
    #         # _logger.dbug('FGF bank_account_no %s' % (bank_account_no))
    #         try:
    #             a = iban.validate(bank_account_no)
    #         except:
    #             raise ValidationError(_('%s is not a valid IBAN.') % (bank_account_no))
    #         res = iban.format(a)
    #     return res

    # @api.onchange('bank_account_no')
    # def onchange_acc_id(self):
    #     result = {}
    #     if self.bank_account_no:
    #         result['bank_account_no'] = self._format_iban(self.bank_account_no)

    #     return {'value': result}

    # @api.onchange('job_id')
    # def onchange_job_id(self):
    #     if self.job_id:
    #         self.job_title = self.job_id.name

    def get_finanical_deduct_amount(self):
        for rec in self:
            amount = 0.0
            _logger.info('_______________ id : %s ' % self.name)
            records = self.env['hr.financial.deduct'].sudo().search(
                [('state', '=', 'approve'), ('employee_id', '=', self.id)])
            _logger.info('_______________ records: %s ' % records)
            if records:
                for i in records:
                    amount += i.deduct_amount
            _logger.info('_______________ amount: %s ' % amount)
            # return amount     

    # opening balance
    eos_opening = fields.Float('End Of Service Opening Balance')
    eos_running_balance = fields.Float('End Of Service Monthly Balance')
    leave_opening = fields.Float('Leave Opening Balance')
    leave_running_balance = fields.Float('Leave Monthly Balance', store=True)

    ticket_opening = fields.Float('Ticket Opening Balance')
    ticket_running_balance = fields.Float('Ticket Monthly Balance', store=True)

    total_balance = fields.Float()

    # @api.depends('name')
    # def compute_monthly_balance(self):
    #     for employee in self:

    #             employee.eos_running_balance = 0.00
    #             employee.total_balance += employee.eos_running_balance


class EmployeeRelationInfo(models.Model):
    """Table for keep employee family information"""
    _name = 'hr.employee.relation'

    name = fields.Char(string="Relationship",
                       help="Relationship with thw employee")


class HRCertificates(models.Model):
    _name = 'hr.certificates'

    name = fields.Char(string="Name")


class HrEmployeeFamilyInfo(models.Model):
    """Table for keep employee family information"""
    _name = 'hr.employee.family'
    _description = 'HR Employee Family'

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  help='Select corresponding Employee',
                                  invisible=1)
    relation_id = fields.Many2one('hr.employee.relation', string="Relation Type", help="Relationship with the employee")
    member_name = fields.Char(string='Name')
    member_contact = fields.Char(string='Mobile Number')
    member_identification_id = fields.Char(string='ID Number/Iqama')
    birth_date = fields.Date(string="Birth Date", tracking=True)
    insurance_amount = fields.Float(string='Amount')

    insurance_duration = fields.Selection(string="Insurance Duration",
                                          selection=[('day', 'Day'), ('month', 'Month'), ('year', 'Year')],
                                          )
    insurance_quantity = fields.Integer(string="Insurance Quantity")


class OtherFees(models.Model):
    _name = 'other.fees'
    _description = 'Other Fees'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(string="Name")
    amount = fields.Float(string="Amount")


class InsuranceTerms(models.Model):
    """Table for keep employee family information"""
    _name = 'hr.insurance.terms'
    rec_name = 'insurance_company'
    _description = 'HR Insurance Terms'

    insurance_company = fields.Char(string='Insurance Company')

    start_date = fields.Date('Start Date')
    expire_date = fields.Date('Expiry Date')
    active = fields.Boolean()
