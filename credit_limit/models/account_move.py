from odoo import api, fields, models , _
from odoo.exceptions import ValidationError
from datetime import datetime,date,timedelta




class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    is_days = fields.Boolean(
        string='Is Days',
        required=False)

    days_number = fields.Integer(
        string='Days Number',
        required=False)

class AccountMove(models.Model):
    _inherit = 'account.move'

    end_terms_days = fields.Date(
        string='', 
        required=False)

    @api.onchange('invoice_payment_term_id')
    def onchange_invoice_payment_term_id(self):
        if self.invoice_payment_term_id.is_days == True:
            days = self.invoice_payment_term_id.days_number
            self.end_terms_days = self.create_date.date() + timedelta(days=days)

    def action_post(self):
        res = super().action_post()
        if self.partner_id.credit_type == 'credit_limit_in_days':
            last_invoices = self.env['account.move'].search([('end_terms_days', '>', fields.Date.today()), ('payment_ids', '=', False)])
            if len(last_invoices) > 0:
                raise ValidationError(_("You Must Pay Your Last Invoices"))

        else:
            if self.partner_id.credit_type == 'advanced':
                config_setting = self.env['res.config.settings'].search([], limit=1, order="id desc")
                if config_setting.account_default_credit_limit >= self.amount_total:
                    return res
                else:
                    raise ValidationError(_("You Must Increase Your Balance"))
    
            if self.partner_id.credit_type == 'credit_limit':
                if self.partner_id.use_partner_credit_limit == True and self.partner_id.credit_limit > self.amount_total:
                    return res
                else:
                    raise ValidationError(_("You Cannot Take More Than Tour limit"))
    
    
    
